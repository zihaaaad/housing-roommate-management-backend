from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload
from app.core.exceptions import BadRequestException, ConflictException, ForbiddenException, ResourceNotFoundException
from app.models.notification import Notification
from app.models.profile import UserProfile
from app.models.roommate_request import RoommateRequest
from app.models.user import User
from app.schemas.auth import UserSummaryResponse
from app.schemas.common import NotificationType, RoommateRequestStatus
from app.schemas.profile import UserProfileResponse
from app.schemas.roommate import (
    RoommateCompatibilityScore,
    RoommateMatchResponse,
    RoommateRequestCreate,
    RoommateRequestStatusUpdate,
)


class RoommateMatchingService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_compatibility(
        self,
        seeker_profile: UserProfile,
        candidate_profile: UserProfile
    ) -> RoommateCompatibilityScore:
        budget_score = 50.0
        seeker_min = seeker_profile.budget_min
        seeker_max = seeker_profile.budget_max
        candidate_min = candidate_profile.budget_min
        candidate_max = candidate_profile.budget_max

        if seeker_max > 0 and candidate_max > 0:
            overlap_min = max(seeker_min, candidate_min)
            overlap_max = min(seeker_max, candidate_max)
            if overlap_min <= overlap_max:
                budget_score = 100.0
            else:
                difference = overlap_min - overlap_max
                midpoint = (seeker_max + candidate_max) / 2.0
                if midpoint > 0:
                    ratio = max(0.0, 1.0 - (difference / midpoint))
                    budget_score = round(ratio * 100.0, 1)
                else:
                    budget_score = 50.0

        location_score = 40.0
        if seeker_profile.preferred_city and candidate_profile.preferred_city:
            if seeker_profile.preferred_city.strip().lower() == candidate_profile.preferred_city.strip().lower():
                location_score = 100.0
                if (
                    seeker_profile.preferred_neighborhood and
                    candidate_profile.preferred_neighborhood and
                    seeker_profile.preferred_neighborhood.strip().lower() != candidate_profile.preferred_neighborhood.strip().lower()
                ):
                    location_score = 85.0
            else:
                location_score = 10.0

        cleanliness_matrix = {
            ("VERY_CLEAN", "VERY_CLEAN"): 100.0,
            ("VERY_CLEAN", "MODERATE"): 70.0,
            ("VERY_CLEAN", "RELAXED"): 20.0,
            ("MODERATE", "MODERATE"): 100.0,
            ("MODERATE", "RELAXED"): 75.0,
            ("RELAXED", "RELAXED"): 100.0,
        }
        cleanliness_pair = tuple(sorted([seeker_profile.cleanliness_level, candidate_profile.cleanliness_level]))
        cleanliness_score = cleanliness_matrix.get(cleanliness_pair, 70.0)

        if seeker_profile.sleep_schedule == candidate_profile.sleep_schedule:
            sleep_schedule_score = 100.0
        elif seeker_profile.sleep_schedule == "FLEXIBLE" or candidate_profile.sleep_schedule == "FLEXIBLE":
            sleep_schedule_score = 85.0
        else:
            sleep_schedule_score = 30.0

        smoking_match = 100.0
        if seeker_profile.smoking_habit == candidate_profile.smoking_habit:
            smoking_match = 100.0
        elif seeker_profile.smoking_habit == "NON_SMOKER" and candidate_profile.smoking_habit == "SMOKER":
            smoking_match = 15.0
        elif seeker_profile.smoking_habit == "SMOKER" and candidate_profile.smoking_habit == "NON_SMOKER":
            smoking_match = 15.0
        else:
            smoking_match = 60.0

        pet_match = 100.0
        if seeker_profile.pet_habit == candidate_profile.pet_habit:
            pet_match = 100.0
        elif seeker_profile.pet_habit == "PET_FRIENDLY" or candidate_profile.pet_habit == "PET_FRIENDLY":
            pet_match = 90.0
        elif (seeker_profile.pet_habit == "NO_PETS" and candidate_profile.pet_habit == "HAS_PETS") or (
            seeker_profile.pet_habit == "HAS_PETS" and candidate_profile.pet_habit == "NO_PETS"
        ):
            pet_match = 15.0
        else:
            pet_match = 70.0

        habits_score = round((smoking_match + pet_match) / 2.0, 1)

        party_matrix = {
            ("RARELY", "RARELY"): 100.0,
            ("RARELY", "OCCASIONALLY"): 70.0,
            ("RARELY", "FREQUENTLY"): 20.0,
            ("OCCASIONALLY", "OCCASIONALLY"): 100.0,
            ("OCCASIONALLY", "FREQUENTLY"): 75.0,
            ("FREQUENTLY", "FREQUENTLY"): 100.0,
        }
        party_pair = tuple(sorted([seeker_profile.party_habit, candidate_profile.party_habit]))
        party_score = party_matrix.get(party_pair, 70.0)

        overall_score = round(
            (budget_score * 0.25) +
            (location_score * 0.20) +
            (cleanliness_score * 0.15) +
            (sleep_schedule_score * 0.15) +
            (habits_score * 0.15) +
            (party_score * 0.10),
            1
        )

        return RoommateCompatibilityScore(
            overall_score=overall_score,
            budget_score=budget_score,
            location_score=location_score,
            cleanliness_score=cleanliness_score,
            sleep_schedule_score=sleep_schedule_score,
            habits_score=habits_score,
            party_score=party_score
        )

    def find_compatible_roommates(
        self,
        current_user: User,
        target_city: Optional[str] = None,
        minimum_score: float = 0.0,
        limit: int = 20
    ) -> List[RoommateMatchResponse]:
        seeker_profile = self.db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not seeker_profile:
            seeker_profile = UserProfile(user_id=current_user.id)
            self.db.add(seeker_profile)
            self.db.commit()
            self.db.refresh(seeker_profile)

        effective_city = target_city or seeker_profile.preferred_city

        candidate_query = self.db.query(User).join(UserProfile).options(
            joinedload(User.profile)
        ).filter(
            User.id != current_user.id,
            User.is_active == True,
            User.role.in_(["ROOMMATE_SEEKER", "TENANT"])
        )

        if effective_city:
            candidate_query = candidate_query.filter(
                func.lower(UserProfile.preferred_city) == effective_city.strip().lower()
            )

        candidates = candidate_query.all()
        scored_candidates: List[RoommateMatchResponse] = []

        for candidate in candidates:
            if not candidate.profile:
                continue

            score = self.calculate_compatibility(seeker_profile, candidate.profile)
            if score.overall_score >= minimum_score:
                scored_candidates.append(
                    RoommateMatchResponse(
                        user=UserSummaryResponse.model_validate(candidate),
                        profile=UserProfileResponse.model_validate(candidate.profile),
                        compatibility=score
                    )
                )

        scored_candidates.sort(key=lambda match: match.compatibility.overall_score, reverse=True)
        return scored_candidates[:limit]

    def send_roommate_request(
        self,
        current_user: User,
        payload: RoommateRequestCreate
    ) -> RoommateRequest:
        if current_user.id == payload.recipient_id:
            raise BadRequestException("You cannot send a roommate request to yourself.")

        recipient = self.db.query(User).filter(User.id == payload.recipient_id).first()
        if not recipient:
            raise ResourceNotFoundException("User", payload.recipient_id)

        existing_pending = self.db.query(RoommateRequest).filter(
            RoommateRequest.requester_id == current_user.id,
            RoommateRequest.recipient_id == payload.recipient_id,
            RoommateRequest.status == "PENDING"
        ).first()
        if existing_pending:
            raise ConflictException("A pending roommate request already exists with this user.")

        new_request = RoommateRequest(
            requester_id=current_user.id,
            recipient_id=payload.recipient_id,
            property_id=payload.property_id,
            message=payload.message,
            status="PENDING"
        )
        self.db.add(new_request)
        self.db.flush()

        notification = Notification(
            recipient_id=payload.recipient_id,
            title="New Roommate Request",
            message=f"{current_user.full_name} sent you a roommate request.",
            notification_type=NotificationType.ROOMMATE_REQUEST.value,
            reference_id=str(new_request.id)
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(new_request)
        return new_request

    def update_request_status(
        self,
        request_id: int,
        current_user: User,
        payload: RoommateRequestStatusUpdate
    ) -> RoommateRequest:
        roommate_request = self.db.query(RoommateRequest).options(
            joinedload(RoommateRequest.requester),
            joinedload(RoommateRequest.recipient)
        ).filter(RoommateRequest.id == request_id).first()

        if not roommate_request:
            raise ResourceNotFoundException("RoommateRequest", request_id)

        target_status = payload.status.value

        if target_status == "CANCELLED":
            if roommate_request.requester_id != current_user.id:
                raise ForbiddenException("Only the requester can cancel this roommate request.")
        else:
            if roommate_request.recipient_id != current_user.id:
                raise ForbiddenException("Only the recipient can respond to this roommate request.")

        roommate_request.status = target_status
        if payload.response_message:
            roommate_request.response_message = payload.response_message
        roommate_request.updated_at = datetime.now(timezone.utc)

        notify_user_id = (
            roommate_request.recipient_id if target_status == "CANCELLED"
            else roommate_request.requester_id
        )
        status_notification = Notification(
            recipient_id=notify_user_id,
            title="Roommate Request Updated",
            message=f"Your roommate request status was changed to {target_status} by {current_user.full_name}.",
            notification_type=NotificationType.ROOMMATE_REQUEST.value,
            reference_id=str(roommate_request.id)
        )
        self.db.add(status_notification)
        self.db.commit()
        self.db.refresh(roommate_request)
        return roommate_request

    def get_user_roommate_requests(
        self,
        user_id: int,
        folder_type: str = "received"
    ) -> List[RoommateRequest]:
        query = self.db.query(RoommateRequest).options(
            joinedload(RoommateRequest.requester),
            joinedload(RoommateRequest.recipient)
        )
        if folder_type == "sent":
            query = query.filter(RoommateRequest.requester_id == user_id)
        else:
            query = query.filter(RoommateRequest.recipient_id == user_id)

        return query.order_by(RoommateRequest.created_at.desc()).all()

    def delete_roommate_request(self, request_id: int, current_user: User) -> None:
        roommate_request = self.db.query(RoommateRequest).filter(RoommateRequest.id == request_id).first()
        if not roommate_request:
            raise ResourceNotFoundException("RoommateRequest", request_id)
        if roommate_request.requester_id != current_user.id and current_user.role != "ADMIN":
            raise ForbiddenException("Unauthorized to delete this roommate request.")
        self.db.delete(roommate_request)
        self.db.commit()

