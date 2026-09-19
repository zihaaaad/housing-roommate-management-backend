from datetime import datetime, timedelta, timezone
from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models.application import RentalApplication
from app.models.inquiry import PropertyInquiry
from app.models.notification import Notification
from app.models.profile import UserProfile
from app.models.property import Property
from app.models.room import Room
from app.models.roommate_request import RoommateRequest
from app.models.user import User


def seed_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    admin_user = User(
        email="admin@housing.com",
        username="admin",
        full_name="Platform Administrator",
        phone_number="+8801711000001",
        role="ADMIN",
        hashed_password=hash_password("Admin@123456"),
        is_active=True,
        is_verified=True
    )
    db.add(admin_user)

    landlord_one = User(
        email="rafiq.landlord@housing.com",
        username="rafiq_landlord",
        full_name="Rafiqul Islam",
        phone_number="+8801711010101",
        role="LANDLORD",
        hashed_password=hash_password("Landlord@123456"),
        is_active=True,
        is_verified=True
    )
    db.add(landlord_one)

    landlord_two = User(
        email="nasreen.landlord@housing.com",
        username="nasreen_landlord",
        full_name="Nasreen Akter",
        phone_number="+8801819010202",
        role="LANDLORD",
        hashed_password=hash_password("Landlord@123456"),
        is_active=True,
        is_verified=True
    )
    db.add(landlord_two)

    seeker_tanvir = User(
        email="tanvir.hasan@seeker.com",
        username="tanvir_hasan",
        full_name="Tanvir Hasan",
        phone_number="+8801712020101",
        role="ROOMMATE_SEEKER",
        hashed_password=hash_password("Seeker@123456"),
        is_active=True,
        is_verified=True
    )
    db.add(seeker_tanvir)

    seeker_arif = User(
        email="arif.rahman@seeker.com",
        username="arif_rahman",
        full_name="Arif Rahman",
        phone_number="+8801812020202",
        role="ROOMMATE_SEEKER",
        hashed_password=hash_password("Seeker@123456"),
        is_active=True,
        is_verified=True
    )
    db.add(seeker_arif)

    seeker_sadia = User(
        email="sadia.chowdhury@seeker.com",
        username="sadia_chowdhury",
        full_name="Sadia Chowdhury",
        phone_number="+8801913020303",
        role="TENANT",
        hashed_password=hash_password("Seeker@123456"),
        is_active=True,
        is_verified=True
    )
    db.add(seeker_sadia)

    db.commit()

    now = datetime.now(timezone.utc)

    tanvir_profile = UserProfile(
        user_id=seeker_tanvir.id,
        bio="Software engineer working at a tech company in Karwan Bazar. Enjoys quiet evenings, reading, and tea.",
        occupation="Software Engineer",
        age=26,
        gender="Male",
        budget_min=8000.0,
        budget_max=15000.0,
        preferred_city="Dhaka",
        preferred_neighborhood="Dhanmondi",
        cleanliness_level="VERY_CLEAN",
        sleep_schedule="EARLY_BIRD",
        smoking_habit="NON_SMOKER",
        pet_habit="PET_FRIENDLY",
        party_habit="RARELY",
        dietary_preference="OMNIVORE",
        work_status="HYBRID",
        move_in_date=now + timedelta(days=15)
    )
    db.add(tanvir_profile)

    arif_profile = UserProfile(
        user_id=seeker_arif.id,
        bio="Product designer at an IT firm in Banani. Social, friendly, keeps living space neat and organized.",
        occupation="Product Designer",
        age=28,
        gender="Male",
        budget_min=9000.0,
        budget_max=16000.0,
        preferred_city="Dhaka",
        preferred_neighborhood="Dhanmondi",
        cleanliness_level="VERY_CLEAN",
        sleep_schedule="EARLY_BIRD",
        smoking_habit="NON_SMOKER",
        pet_habit="PET_FRIENDLY",
        party_habit="OCCASIONALLY",
        dietary_preference="OMNIVORE",
        work_status="HYBRID",
        move_in_date=now + timedelta(days=20)
    )
    db.add(arif_profile)

    sadia_profile = UserProfile(
        user_id=seeker_sadia.id,
        bio="Graduate student at University of Dhaka. Quiet, spends most time studying or doing research.",
        occupation="Graduate Student",
        age=24,
        gender="Female",
        budget_min=6000.0,
        budget_max=11000.0,
        preferred_city="Dhaka",
        preferred_neighborhood="Mirpur",
        cleanliness_level="MODERATE",
        sleep_schedule="NIGHT_OWL",
        smoking_habit="NON_SMOKER",
        pet_habit="NO_PETS",
        party_habit="RARELY",
        dietary_preference="ANY",
        work_status="STUDENT",
        move_in_date=now + timedelta(days=30)
    )
    db.add(sadia_profile)

    db.commit()

    property_one = Property(
        landlord_id=landlord_one.id,
        title="3-Bedroom Family Flat in Dhanmondi",
        description="Spacious flat with high-speed internet, elevator, 24-hour generator backup, and south-facing balcony.",
        property_type="APARTMENT",
        address="House 42, Road 8A, Dhanmondi",
        city="Dhaka",
        state="Dhaka Division",
        postal_code="1209",
        country="Bangladesh",
        total_bedrooms=3,
        total_bathrooms=3,
        square_feet=1550,
        furnished_status="FURNISHED",
        is_pet_friendly=True,
        is_smoking_allowed=False,
        parking_available=True,
        amenities="WIFI,ELEVATOR,GENERATOR_BACKUP,BALCONY,SECURITY_GUARD",
        base_monthly_rent=32000.0,
        security_deposit=32000.0,
        utilities_included=True,
        available_from=now + timedelta(days=5),
        lease_duration_months=12,
        status="AVAILABLE",
        image_urls="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00,https://images.unsplash.com/photo-1512917774080-9991f1c4c750"
    )
    db.add(property_one)

    property_two = Property(
        landlord_id=landlord_two.id,
        title="Bachelor Sublet Flat in Bashundhara R/A",
        description="Flat with rooftop access, security guard, and bike parking in a quiet residential sector.",
        property_type="SHARED_FLAT",
        address="Plot 118, Road 4, Block C, Bashundhara R/A",
        city="Dhaka",
        state="Dhaka Division",
        postal_code="1229",
        country="Bangladesh",
        total_bedrooms=3,
        total_bathrooms=2,
        square_feet=1400,
        furnished_status="SEMI_FURNISHED",
        is_pet_friendly=True,
        is_smoking_allowed=False,
        parking_available=True,
        amenities="WIFI,ROOFTOP,SECURITY_GUARD,WATER_FILTER,CCTV",
        base_monthly_rent=24000.0,
        security_deposit=24000.0,
        utilities_included=False,
        available_from=now + timedelta(days=10),
        lease_duration_months=12,
        status="AVAILABLE",
        image_urls="https://images.unsplash.com/photo-1518780664697-55e3ad937233"
    )
    db.add(property_two)

    property_three = Property(
        landlord_id=landlord_one.id,
        title="Studio Apartment near GEC Circle",
        description="Studio flat close to universities, shopping centers, and bus routes.",
        property_type="STUDIO",
        address="12 CDA Avenue, GEC Circle",
        city="Chittagong",
        state="Chittagong Division",
        postal_code="4000",
        country="Bangladesh",
        total_bedrooms=1,
        total_bathrooms=1,
        square_feet=550,
        furnished_status="FURNISHED",
        is_pet_friendly=False,
        is_smoking_allowed=False,
        parking_available=True,
        amenities="WIFI,AIR_CONDITIONING,GENERATOR_BACKUP",
        base_monthly_rent=14000.0,
        security_deposit=14000.0,
        utilities_included=True,
        available_from=now + timedelta(days=7),
        lease_duration_months=6,
        status="AVAILABLE",
        image_urls="https://images.unsplash.com/photo-1502672260266-1c1ef2d93688"
    )
    db.add(property_three)

    db.commit()

    room_one = Room(
        property_id=property_one.id,
        room_name="Master Bedroom with Attached Balcony & Bath",
        room_type="MASTER_WITH_BATH",
        monthly_rent=13500.0,
        security_deposit=13500.0,
        is_available=True,
        private_bathroom=True,
        square_feet=240,
        available_date=now + timedelta(days=5)
    )
    db.add(room_one)

    room_two = Room(
        property_id=property_one.id,
        room_name="South Facing Single Bedroom",
        room_type="SINGLE",
        monthly_rent=10500.0,
        security_deposit=10500.0,
        is_available=True,
        private_bathroom=False,
        square_feet=180,
        available_date=now + timedelta(days=5)
    )
    db.add(room_two)

    db.commit()

    inquiry = PropertyInquiry(
        property_id=property_one.id,
        applicant_id=seeker_tanvir.id,
        scheduled_viewing_date=now + timedelta(days=3),
        status="CONFIRMED",
        notes="Interested in the master bedroom with balcony.",
        landlord_notes="Confirmed for Friday afternoon."
    )
    db.add(inquiry)

    application = RentalApplication(
        property_id=property_one.id,
        room_id=room_one.id,
        applicant_id=seeker_tanvir.id,
        proposed_move_in_date=now + timedelta(days=15),
        lease_duration_months=12,
        monthly_income=75000.0,
        credit_score=750,
        employment_status="Full-time Software Engineer",
        emergency_contact_name="Kamal Hossain",
        emergency_contact_phone="+8801711998877",
        status="PENDING"
    )
    db.add(application)

    roommate_req = RoommateRequest(
        requester_id=seeker_tanvir.id,
        recipient_id=seeker_arif.id,
        property_id=property_one.id,
        status="PENDING",
        message="Hi Arif, our budgets and schedules match well. Would you like to share the flat in Dhanmondi?"
    )
    db.add(roommate_req)

    notif = Notification(
        recipient_id=seeker_arif.id,
        title="New Roommate Request",
        message="Tanvir Hasan sent you a roommate request.",
        notification_type="ROOMMATE_REQUEST",
        reference_id=str(roommate_req.id)
    )
    db.add(notif)

    db.commit()
    db.close()


if __name__ == "__main__":
    seed_database()
