import argparse
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app, db, get_or_create_default_event  # noqa: E402
from models import Gift, RelationshipCategory  # noqa: E402


DEFAULT_COUNT = 250
DEFAULT_SEED = 20260612
DEFAULT_RELATIONS = ["가족", "친척", "친구", "직장", "지인", "기타"]
CUSTOM_RELATIONS = ["동아리", "대학교", "전 직장", "부모님 지인", "모임"]
SIDES = ["신부측", "신랑측"]

SURNAMES = [
    "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임",
    "한", "오", "서", "신", "권", "황", "안", "송", "류", "홍",
]
GIVEN_NAMES = [
    "민수", "서연", "지훈", "유진", "현우", "지민", "수빈", "도윤", "하은", "준호",
    "예린", "성민", "나영", "시우", "채원", "동현", "혜진", "재윤", "은지", "태민",
    "민지", "서준", "지우", "예준", "다은", "유나", "현지", "승현", "소연", "준영",
]
MEMOS = [
    "신부 친구",
    "아버지 지인",
    "회사 동료",
    "동아리 선배",
    "나중에 확인 필요",
    "어머니 지인",
    "대학교 동기",
    "전 직장 동료",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="개발/테스트용 축의금 더미 데이터를 생성합니다."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_COUNT,
        help=f"생성할 active Gift 수입니다. 기본값: {DEFAULT_COUNT}",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="기존 Gift와 RelationshipCategory 데이터를 삭제한 뒤 생성합니다.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="--reset 확인 입력을 생략합니다. 자동 테스트용입니다.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"랜덤 seed입니다. 기본값: {DEFAULT_SEED}",
    )
    return parser.parse_args()


def describe_database():
    database_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    print(f"DB URI: {database_uri}")

    if database_uri.startswith("sqlite:///"):
        db_path = database_uri.replace("sqlite:///", "", 1)
        print(f"SQLite path: {Path(db_path).resolve()}")


def confirm_reset():
    answer = input("정말 기존 데이터를 삭제하고 더미 데이터를 생성할까요? yes 입력 시 진행: ")
    return answer.strip().lower() == "yes"


def weighted_choice(rng, weighted_values):
    values = [value for value, _weight in weighted_values]
    weights = [weight for _value, weight in weighted_values]
    return rng.choices(values, weights=weights, k=1)[0]


def make_name(rng, index):
    surname = rng.choice(SURNAMES)
    given_name = GIVEN_NAMES[index % len(GIVEN_NAMES)]
    return f"{surname}{given_name}"


def make_amount(rng):
    return weighted_choice(
        rng,
        [
            (50_000, 6),
            (100_000, 38),
            (200_000, 28),
            (300_000, 14),
            (500_000, 10),
            (1_000_000, 4),
        ],
    )


def make_meal_ticket_count(rng):
    return weighted_choice(
        rng,
        [
            (0, 10),
            (1, 52),
            (2, 30),
            (3, 7),
            (4, 1),
        ],
    )


def make_relation(rng):
    return weighted_choice(
        rng,
        [
            ("가족", 5),
            ("친척", 20),
            ("친구", 24),
            ("직장", 18),
            ("지인", 16),
            ("기타", 5),
            ("", 7),
            ("동아리", 2),
            ("대학교", 1),
            ("전 직장", 1),
            ("부모님 지인", 1),
            ("모임", 1),
        ],
    )


def make_memo(rng, relation):
    if rng.random() >= 0.18:
        return ""

    if relation == "친구":
        return rng.choice(["신부 친구", "신랑 친구", "고등학교 친구"])

    if relation == "직장":
        return rng.choice(["회사 동료", "같은 팀", "거래처"])

    if relation in CUSTOM_RELATIONS:
        return rng.choice(["동아리 선배", "대학교 동기", "모임 지인", "전 직장 동료"])

    return rng.choice(MEMOS)


def create_relationship_categories(event_id):
    for sort_order, name in enumerate(CUSTOM_RELATIONS, start=1):
        db.session.add(
            RelationshipCategory(
                event_id=event_id,
                name=name,
                sort_order=sort_order,
            )
        )


def create_gift(event_id, envelope_numbers, rng, index, deleted=False):
    side = "신부측" if rng.random() < 0.55 else "신랑측"
    envelope_numbers[side] += 1
    relation = make_relation(rng)
    created_at = datetime.now() - timedelta(minutes=(index * 3))
    deleted_at = datetime.now() if deleted else None

    return Gift(
        event_id=event_id,
        envelope_no=envelope_numbers[side],
        name=make_name(rng, index),
        side=side,
        relation=relation,
        amount=make_amount(rng),
        meal_ticket_count=make_meal_ticket_count(rng),
        memo=make_memo(rng, relation),
        created_at=created_at,
        updated_at=created_at,
        deleted_at=deleted_at,
    )


def seed_dummy_data(count, seed):
    rng = random.Random(seed)
    event = get_or_create_default_event()
    envelope_numbers = {side: 0 for side in SIDES}

    create_relationship_categories(event.id)

    gifts = [
        create_gift(event.id, envelope_numbers, rng, index)
        for index in range(count)
    ]
    deleted_sample_count = min(5, max(0, count // 50))
    deleted_gifts = [
        create_gift(event.id, envelope_numbers, rng, count + index, deleted=True)
        for index in range(deleted_sample_count)
    ]

    db.session.add_all(gifts + deleted_gifts)
    db.session.commit()

    bride_count = sum(1 for gift in gifts if gift.side == "신부측")
    groom_count = sum(1 for gift in gifts if gift.side == "신랑측")
    unclassified_count = sum(1 for gift in gifts if not (gift.relation or "").strip())

    print("더미 데이터 생성 완료")
    print(f"총 생성(active): {len(gifts)}건")
    print(f"신부측: {bride_count}건")
    print(f"신랑측: {groom_count}건")
    print(f"사용자 추가 관계: {', '.join(CUSTOM_RELATIONS)}")
    print(f"미분류: {unclassified_count}건")
    print(f"삭제 샘플: {len(deleted_gifts)}건")
    print(f"랜덤 seed: {seed}")


def main():
    args = parse_args()

    if args.count <= 0:
        print("--count는 1 이상의 숫자여야 합니다.")
        return 1

    with app.app_context():
        db.create_all()
        describe_database()

        existing_gift_count = Gift.query.count()
        existing_category_count = RelationshipCategory.query.count()

        if existing_gift_count > 0 and not args.reset:
            print("이미 축의금 내역이 존재합니다.")
            print("기존 데이터를 지우고 더미 데이터를 생성하려면 --reset 옵션을 사용하세요.")
            print(f"현재 Gift: {existing_gift_count}건")
            print(f"현재 RelationshipCategory: {existing_category_count}건")
            return 1

        if args.reset:
            print(f"삭제 대상 Gift: {existing_gift_count}건")
            print(f"삭제 대상 RelationshipCategory: {existing_category_count}건")

            if not args.yes and not confirm_reset():
                print("작업을 취소했습니다.")
                return 1

            Gift.query.delete()
            RelationshipCategory.query.delete()
            db.session.commit()
            print("기존 Gift / RelationshipCategory 데이터를 삭제했습니다.")

        seed_dummy_data(args.count, args.seed)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
