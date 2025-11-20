from sqlalchemy import ( Column, BigInteger, String, Integer, Date, DateTime, Boolean, Enum)
from sqlalchemy.sql import func
from app.db.database import Base
from datetime import datetime, timezone

# dabin
# User : 인증 / 식별 정보만 저장
class User(Base):
    __tablename__ = "users"  # MySql에서 작성한 users테이블과 매핑 -> PG

    id = Column(             # id Query
        BigInteger,          # BIGINT -> PostgreSQL (PG)
        primary_key=True,    # PRIMARY_KEY
        autoincrement=True  #postgres는 없는게아니라 꼭있어야한다네요 -hyunjun
    )

    email = Column(          # email Query
        String(255),         # VARCHAR
        unique=True,         # UNIQUE
        nullable=False       # NOT NULL
    )
    
    username = Column(       # username Query
        String(50),          # VARCHAR
        unique=True,         # UNIQUE
        nullable=False       # NOT NULL
    )

    password = Column(  # passowrd Query
        String(255),         # VARCHAR
        nullable=False       # NOT NULL 
    )
    # nickname user_info(front와 이름통일 필요)로 이전 - hyunjun

    created_at = Column(          # created_at Query        
        DateTime(timezone=True),
        nullable=False,           # NOT NULL
        default=lambda: datetime.now(timezone.utc) # DEFAULT CURRENT_TIMESTAMP -> 
    )
    # 개발편의성 updated_at / 디버깅 , front UX, 병렬요청 충돌 방지?
    # updated_at = Column(
    #     DateTime(timezone=True),
    #     nullable=True,
    #     default=lambda: datetime.now(timezone.utc),
    #     onupdate=lambda: datetime.now(timezone.utc)
    # )

    # social 연동시 활성화
    # provider = Column(       # provider Query
    #     String(50),          # VARCHAR
    #     nullable=False,      # NOT NULL
    #     default="Email"      # DEFAULT "Email" -> 이메일 문자열
    # )

    # ===================================================
    # 최소기능구현 후 확장    

    # phone 초기요구필드엔 없음 -hyunjun
    # phone = Column(          # phone Query
    #     String(20),          # VARCHAR
    #     unique=True          # UNIQUE
    # )

    # is_active = Column(      # is_active Query
    #     Boolean,             # TINYINT(1) (1 -> True, 0 -> False)
    #     nullable=False,      # NOT NULL
    #     default=True         # DEFAULT 1 (1 -> True, 0 -> False)
    # )
    #기초단계 구현 x
    # email_verified = Column( # email_verified Query
    #     Boolean,             # TINYINT(1) (1 -> True, 0 -> False)
    #     nullable=True,      # NOT NULL 차후 활성 -hyunjun
    #     default=False        # DEFAULT 0 (1 -> True, 0 -> False)
    # )


    # 기본기능 안정화 후 구현 
    # login_fail_count = Column(    # login_fail_count Query
    #     Integer,                  # INT
    #     nullable=False,           # NOT NULL
    #     default=0                 # DEFAULT 0 -> 단순 횟수이기 때문에 0
    # )

    # locked_until = Column(        # locked_until Query
    #     DateTime,                 # DATETIME
    #     nullable=True             # NULL
    # )

    # Postgres 사용예정입니다 - hyujnun
    # ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    # ENGINE=InnoDB은 기본값이기 때문에 따로 적을 필요가 없음
    # DEFAULT CHARSET=utf8mb4 또한 기본값이기 때문에 따로 적을 필요가 없음

    
    # user profile, userhealthcondition은 추후 추가 예정
