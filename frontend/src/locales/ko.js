/**
 * 한국어 번역 파일
 *
 * 사용 방법:
 * - 템플릿: {{ $t('common.button.save') }}
 * - 스크립트: const { t } = useI18n(); t('common.button.save')
 * - 변수 포함: {{ $t('welcome.message', { name: username }) }}
 *
 * 구조:
 * - 중첩 객체로 관리 (카테고리.영역.항목)
 * - 명확하고 설명적인 키 이름 사용
 */

export default {
  // ============================================
  // 공통 UI 요소 (Common)
  // ============================================
  common: {
    // 버튼
    button: {
      save: '저장',
      saving: '저장 중...',
      cancel: '취소',
      edit: '수정',
      delete: '삭제',
      add: '추가',
      search: '검색',
      refresh: '새로고침',
      apply: '적용',
      close: '닫기',
      confirm: '확인',
      back: '뒤로',
      backToList: '목록으로',
      next: '다음',
      previous: '이전',
      download: '다운로드',
      upload: '업로드',
      viewAll: '전체보기',
      details: '상세',
      detailedView: '상세 보기'
    },

    // 메시지
    message: {
      loading: '로딩 중...',
      success: '성공적으로 처리되었습니다',
      error: '오류가 발생했습니다',
      noData: '데이터가 없습니다',
      confirmDelete: '정말 삭제하시겠습니까?',
      saved: '저장되었습니다',
      deleted: '삭제되었습니다'
    },

    // 상태
    status: {
      active: '활성',
      inactive: '비활성',
      pending: '대기중',
      approved: '승인됨',
      rejected: '거부됨'
    },

    // 일반 레이블
    title: '제목',
    content: '내용',
    category: '카테고리',
    author: '작성자',
    createdDate: '작성일',
    status: '상태',
    actions: '작업',
    username: '사용자명',
    password: '비밀번호',
    role: '역할',
    notAvailable: 'N/A',
    none: '없음',
    use: '사용',

    // 인증
    auth: {
      loginRequired: '로그인이 필요합니다.'
    },

    // 다크/라이트 모드
    darkMode: '다크 모드',
    lightMode: '라이트 모드'
  },

  // ============================================
  // 네비게이션 (Navigation)
  // ============================================
  nav: {
    home: '홈',
    discover: '스토어',
    tips: '팁&테크',
    settings: '설정',
    more: '더보기',
    favorites: '즐겨찾기',
    scraps: '스크랩',
    admin: '관리',
    changePassword: '비밀번호 변경',
    logout: '로그아웃'
  },

  // ============================================
  // 테마 (Theme)
  // ============================================
  theme: {
    dark: '다크 모드',
    light: '라이트 모드'
  },

  // ============================================
  // 인증 (Authentication)
  // ============================================
  auth: {
    login: {
      title: '로그인',
      username: '사용자명',
      password: '비밀번호',
      submit: '로그인',
      loggingIn: '로그인 중...',
      required: '사용자명과 비밀번호를 입력하세요',
      failed: '로그인에 실패했습니다. 사용자 이름과 비밀번호를 확인하세요.'
    },
    setup: {
      title: '초기 설정',
      createAdmin: '관리자 계정 생성',
      welcome: 'MyApp Store에 오신 것을 환영합니다'
    }
  },

  // ============================================
  // 홈/대시보드 (Home/Dashboard)
  // ============================================
  home: {
    title: '대시보드',
    welcome: '환영합니다! 👋',
    description: '나만의 소프트웨어 라이브러리를 관리하세요',
    recentProducts: '최근 추가된 프로그램',
    loading: '로딩 중...',

    stats: {
      totalProducts: '총 프로그램',
      totalVersions: '총 버전',
      lastScan: '마지막 스캔',
      categoryStats: '카테고리별 통계'
    },

    empty: {
      title: '등록된 프로그램이 없습니다',
      description: '프로그램을 스캔하여 라이브러리를 구축하세요'
    }
  },

  // ============================================
  // 제품 탐색 (Discover)
  // ============================================
  discover: {
    title: '앱 스토어',
    productCount: '개의 프로그램',
    search: '검색',
    searchPlaceholder: '앱 이름, 제조사 검색...',
    filter: '필터',
    categoryFilter: '카테고리',
    filingRules: '정규식 안내',
    violations: '검색된 목록',
    scan: '스캔',

    sort: {
      latest: '최신순',
      name: '이름순',
      category: '카테고리순'
    },

    category: {
      all: '전체',
      graphics: '그래픽',
      office: '오피스',
      development: '개발',
      utility: '유틸리티',
      media: '미디어',
      os: '운영체제',
      security: '보안',
      network: '네트워크',
      mac: '맥',
      mobile: '모바일',
      patch: '패치',
      driver: '드라이버',
      source: '소스',
      backup: '백업&복구',
      business: '업무용',
      engineering: '공학용',
      theme: '테마&스킨',
      font: '글꼴',
      uncategorized: '미분류'
    },

    noResults: {
      title: '검색 결과가 없습니다',
      description: '다른 검색어나 필터를 사용해보세요'
    },

    modal: {
      title: '카테고리'
    }
  },

  // ============================================
  // 제품 상세 (Product Detail)
  // ============================================
  productDetail: {
    visit: '공식 사이트',
    selectCategory: '카테고리 선택',
    logoSearch: '로고 검색',
    iconHint: '아이콘 (클릭하여 검색 가능)',
    imageError: '이미지를 불러올 수 없습니다',

    form: {
      title: '제목',
      subtitle: '부제목',
      vendor: '개발사',
      officialWebsite: '공식 웹사이트'
    },

    tabs: {
      info: '정보',
      versions: '버전',
      screenshots: '스크린샷',
      installation: '설치방법'
    },

    info: {
      description: '프로그램 설명',
      noDescription: '설명이 없습니다.',
      platform: '플랫폼',
      supportSpec: '지원 사양',
      releaseInfo: '릴리즈 정보',
      releaseDate: '릴리즈 날짜',
      releaseNotes: '릴리즈 노트',
      features: '주요 기능',
      noFeatures: '주요 기능 정보가 없습니다.',
      systemRequirements: '시스템 요구사항',
      noSystemRequirements: '시스템 요구사항 정보가 없습니다.',
      supportedFormats: '지원 형식',
      noFormats: '지원 형식 정보가 없습니다.',
      installationInfo: '설치 정보',
      noInstallationInfo: '설치 정보가 없습니다.',
      referenceSites: '참조 사이트 (수동 수정 시 참고)',
      referenceSitesHint: '메타데이터를 수동으로 수정할 때 아래 사이트들을 참고하세요:'
    },

    placeholder: {
      date: '예: 2024-01-15'
    },

    versions: {
      title: '다운로드 가능한 버전',
      version: '버전',
      empty: {
        title: '등록된 버전이 없습니다',
        description: '아직 다운로드 가능한 버전이 없습니다'
      }
    },

    screenshots: {
      title: '스크린샷',
      search: '스크린샷 검색',
      label: '스크린샷',
      delete: '스크린샷 삭제',
      empty: {
        title: '스크린샷이 없습니다',
        description: '이 제품의 스크린샷이 수집되지 않았습니다'
      }
    },

    installation: {
      title: '설치 방법',
      write: '가이드 작성',
      empty: {
        title: '설치 방법이 없습니다',
        description: '위의 \'가이드 작성\' 버튼을 클릭하여 설치 방법을 작성할 수 있습니다'
      }
    }
  },

  // ============================================
  // 팁&테크 (Tips & Tech)
  // ============================================
  tips: {
    title: '💡 팁&테크',
    description: '유용한 팁과 기술 정보를 공유하는 공간입니다',
    write: '글쓰기',
    scrap: '스크랩',
    scrapped: '스크랩됨',
    views: '조회',
    comments: '댓글',

    filter: {
      allCategories: '전체 카테고리'
    },

    category: {
      tip: '팁',
      tech: '기술',
      tutorial: '튜토리얼',
      qna: 'Q&A',
      news: '뉴스'
    },

    sort: {
      latest: '최신순',
      views: '조회수순',
      comments: '댓글순'
    },

    table: {
      number: '번호',
      views: '조회수',
      comments: '댓글',
      createdDate: '작성일'
    },

    badge: {
      notice: '공지',
      new: 'NEW'
    },

    empty: {
      title: '게시글이 없습니다',
      description: '첫 번째 글을 작성해보세요!'
    },

    icon: {
      hasImage: '📷'
    }
  },

  // ============================================
  // 팁&테크 상세 (Tips Detail)
  // ============================================
  tipsDetail: {
    attachments: '첨부파일',
    comments: '댓글',
    commentPlaceholder: '댓글을 입력하세요',
    submitComment: '댓글 작성',

    empty: {
      title: '아직 댓글이 없습니다',
      description: '첫 번째 댓글을 작성해보세요!'
    },

    confirm: {
      deletePost: '정말 이 게시글을 삭제하시겠습니까?',
      deleteComment: '정말 이 댓글을 삭제하시겠습니까?',
      deleteAttachment: '정말 이 첨부파일을 삭제하시겠습니까?'
    },

    dialog: {
      deletePost: '게시글 삭제',
      deleteComment: '댓글 삭제',
      deleteAttachment: '첨부파일 삭제'
    },

    success: {
      deleted: '게시글이 삭제되었습니다.',
      attachmentDeleted: '첨부파일이 삭제되었습니다.'
    },

    error: {
      scrapFailed: '스크랩 처리에 실패했습니다.',
      loadFailed: '게시글을 불러오는데 실패했습니다.'
    },

    validation: {
      commentRequired: '댓글 내용을 입력해주세요.'
    }
  },

  // ============================================
  // 팁&테크 작성 (Tips Write)
  // ============================================
  tipsWrite: {
    new: '글쓰기',
    edit: '글 수정',
    saveDraft: '임시저장',
    submit: '작성하기',
    submitEdit: '수정하기',

    form: {
      category: '카테고리 *',
      categoryPlaceholder: '카테고리를 선택하세요',
      markAsNotice: '공지사항으로 등록',
      titlePlaceholder: '제목을 입력하세요 (최대 100자)',
      tags: '태그 (선택사항)',
      tagsPlaceholder: '태그를 쉼표(,)로 구분하여 입력하세요 (예: windows, 단축키, 팁)',
      tagsHint: '태그는 검색과 분류에 도움이 됩니다',
      attachments: '첨부파일 (선택사항)'
    },

    category: {
      notice: '📢 공지사항',
      tip: '💡 팁',
      tech: '⚙️ 기술',
      tutorial: '📚 튜토리얼',
      qna: '❓ Q&A',
      news: '📰 뉴스'
    },

    file: {
      dragHint: '파일을 드래그 앤 드롭하거나 클릭하여 선택하세요',
      select: '파일 선택',
      limit: '최대 10MB, 최대 5개 파일',
      maxFilesError: '최대 5개의 파일만 첨부할 수 있습니다.',
      sizeError: '의 크기가 너무 큽니다. 최대',
      sizeErrorSuffix: '까지 업로드 가능합니다.',
      duplicateError: '은(는) 이미 추가되었습니다.'
    },

    notice: {
      title: '작성 전 확인사항',
      item1: '제목과 내용이 게시판 주제에 적합한지 확인해주세요',
      item2: '타인을 비방하거나 욕설이 포함된 내용은 삭제될 수 있습니다',
      item3: '저작권을 침해하는 내용은 게시할 수 없습니다'
    },

    confirm: {
      unsavedChanges: '작성 중인 내용이 있습니다. 정말 나가시겠습니까?',
      restoreDraft: '임시저장된 글이 있습니다. 불러오시겠습니까?'
    },

    success: {
      draftSaved: '임시저장되었습니다.',
      created: '게시글이 작성되었습니다.',
      updated: '게시글이 수정되었습니다.'
    },

    validation: {
      categoryRequired: '카테고리를 선택해주세요.',
      titleRequired: '제목을 입력해주세요.',
      contentRequired: '내용을 입력해주세요.'
    }
  },

  // ============================================
  // 설정 (Settings)
  // ============================================
  settings: {
    title: '설정',

    general: {
      title: '일반 설정',
      description: '시스템 설정을 관리합니다',
      section: '시스템 설정',
      language: '언어'
    },

    language: {
      korean: '한국어',
      english: 'English'
    },

    network: {
      title: '네트워크 설정',
      frontendUrl: '프론트엔드 접속 URL',
      frontendUrlHint: '프론트엔드 접속 주소 (예: http://192.168.0.8:5900, http://nas.local:5900)',
      backendUrl: '백엔드 API URL',
      backendUrlHint: '백엔드 API 주소 (예: http://192.168.0.8:8100, http://nas.local:8100)',
      corsOrigins: '추가 허용 도메인 (CORS)',
      corsOriginsHint: '한 줄에 하나씩 입력하세요. 역방향 프록시(NPM, Synology) 사용 시 HTTPS URL을 추가하세요.'
    },

    guide: {
      title: '💡 설정 가이드',
      localNetwork: '로컬 네트워크 접속:',
      localNetworkExample: 'http://내부IP:포트 형식 사용 (예: http://192.168.0.8:5900)',
      reverseProxy: '역방향 프록시 사용 시:',
      reverseProxyExample: 'NPM이나 Synology 역방향 프록시에서 설정한 HTTPS URL 추가',
      docker: 'Docker 환경:',
      dockerExample: 'docker-compose.yml의 CORS_ORIGINS 환경변수도 함께 업데이트 필요',
      afterApply: '설정 적용 후:',
      afterApplyExample: '백엔드 재시작이 필요할 수 있습니다'
    },

    users: {
      title: '사용자 관리',
      description: '사용자를 직접 추가하거나 초대 이메일을 발송할 수 있습니다',
      add: '사용자 추가',
      invite: '사용자 초대',
      systemAdmin: '시스템 관리자',

      role: {
        admin: '관리자',
        user: '일반 사용자'
      }
    },

    folders: {
      title: '폴더 설정',
      description: '스캔할 폴더 경로를 관리합니다',
      add: '폴더 추가',
      scan: '스캔',
      scanning: '스캔중...',
      scanThis: '이 폴더 스캔',
      edit: '변경',

      guide: {
        title: '📁 폴더 추가 방법',
        dockerMount: 'Docker 볼륨 마운트:',
        dockerMountExample: '-v /path/to/your/software:/library/MyFolder',
        symbolicLink: '심볼릭 링크:',
        symbolicLinkExample: 'ln -s /path/to/your/software /library/MyFolder',
        direct: '직접 추가:',
        directExample: '위 버튼으로 폴더를 추가한 후 \'저장\' 버튼 클릭',
        hint: '💡 각 폴더는 독립적으로 스캔할 수 있으며, 변경/삭제 후 반드시 \'저장\' 버튼을 눌러주세요.'
      },

      empty: {
        title: '등록된 폴더가 없습니다',
        description: '위의 \'폴더 추가\' 버튼을 눌러 스캔할 폴더를 추가해주세요.'
      }
    },

    categories: {
      title: '카테고리 관리',
      description: '프로그램 카테고리를 관리합니다',
      add: '카테고리 추가'
    },

    board: {
      title: '게시판 관리',
      description: '팁&테크 게시판 설정을 관리합니다',
      categories: '게시판 카테고리',
      basicSettings: '게시판 기본 설정',
      postsPerPage: '페이지당 게시글 수',
      allowComments: '댓글 허용',
      allowCommentsHint: '게시글에 댓글을 달 수 있습니다',
      allowAttachments: '파일 첨부 허용',
      allowAttachmentsHint: '게시글 작성 시 파일을 첨부할 수 있습니다',

      postsPerPageOptions: {
        10: '10개',
        20: '20개',
        30: '30개',
        50: '50개'
      }
    },

    filingRules: {
      title: '파일명 규칙 안내',
      description: '폴더 및 파일 스캔시 권장하는 파일명 표준 규칙을 확인하세요',
      standardFormat: '표준 형식',
      withVersion: '기본 형식 (버전 있음)',
      formatExample1: '제품명.v버전-기타내용.확장자',
      noVersion: '버전 없는 경우',
      formatExample2: '제품명-기타내용.확장자',
      minimalFormat: '최소 형식',
      formatExample3: '제품명.v버전.확장자',
      formatExample4: '제품명.확장자',
      correctExamples: '올바른 예시',
      pattern1: '패턴 1: 완전한 정보',
      pattern2: '패턴 2: 버전 없음',
      pattern3: '패턴 3: 기본 정보만',
      pattern4: '패턴 4: 제품명만',
      avoidPatterns: '피해야 할 형식',
      avoidReason1: '너무 복잡하고 언더스코어 과다 사용',
      avoidReason2: '제품명이 불분명함',
      avoidReason3: '소문자, 버전 구분자 혼란',
      avoidReason4: '대괄호 입력 불편',
      detailedRules: '세부 규칙',

      productName: {
        title: '1. 제품명 (Product Name)',
        official: '공식 제품명',
        caseInsensitive: '사용 (대소문자 구분)',
        spaces: '띄어쓰기 포함 가능',
        specialChars: '특수문자는 피하기 (',
        excluded: '제외)'
      },

      version: {
        title: '2. 버전 (Version)',
        prefix: '.v',
        prefixRequired: '접두사 사용 (필수)',
        dotOnly: '숫자와 점(',
        dotOnlySuffix: ')만 사용',
        yearAsVersion: '연도도 버전으로 간주 (2023, 2024 등)',
        missingV: '(v 누락)',
        notNumeric: '(숫자가 아님)'
      },

      description: {
        title: '3. 기타내용 (Description)',
        separator: '-',
        separatorUse: '구분자 사용',
        concise: '간단명료하게',
        multiple: '여러 정보는 쉼표 또는 띄어쓰기로 구분'
      },

      conversionExamples: '변환 예시',
      oldFilename: '기존 파일명',
      standardFormatColumn: '표준 형식',

      checklist: {
        title: '파일 업로드 전 체크리스트',
        productName: '제품명이 공식 명칭인가?',
        version: '버전이 있다면',
        versionFormat: '형식인가?',
        description: '기타내용이 있다면',
        descriptionStart: '로 시작하는가?',
        underscore: '언더스코어(',
        underscoreChange: ')를 띄어쓰기로 변경했는가?',
        extension: '확장자가 소문자인가?',
        concise: '파일명이 간결한가? (불필요한 정보 제거)'
      },

      quickReference: '빠른 참조',
      quickRef: {
        full: '완전한 형식:',
        noVersion: '버전 없음:',
        basic: '기본 형식:',
        minimal: '최소 형식:'
      },

      example: '예시:'
    },

    metadata: {
      title: '메타데이터 설정',
      description: 'AI 기반 메타데이터 생성 설정을 관리합니다',
      test: '메타데이터 테스트',
      scanMode: '스캔 방식',
      aiOnly: '🤖 AI 전용',
      aiOnlyDescription: 'AI 모델만 사용하여 메타데이터를 생성합니다',
      modelSettings: 'AI 모델 설정',
      provider: 'AI 제공자',

      openaiModel: 'OpenAI 모델',
      o1Series: 'o1 시리즈 (최신 추론 모델)',
      o1: {
        latest: 'o1 (유료 - 최신 추론)',
        preview: 'o1 Preview (유료 - 미리보기)',
        mini: 'o1 Mini (유료 - 빠름)'
      },

      gpt4o: 'GPT-4o (추천)',
      gpt4oMini: 'GPT-4o Mini (유료 - 저렴, 추천)',
      gpt4oLatest: 'GPT-4o (유료 - 최신)',
      gpt4o20241120: 'GPT-4o (2024-11-20) (유료)',
      gpt4o20240806: 'GPT-4o (2024-08-06) (유료)',
      gpt4o20240513: 'GPT-4o (2024-05-13) (유료)',

      gpt4Turbo: 'GPT-4 Turbo',
      gpt4Turbo: {
        legacy: 'GPT-4 Turbo (유료)',
      },
      gpt4Turbo20240409: 'GPT-4 Turbo (2024-04-09) (유료)',
      gpt4TurboPreview: 'GPT-4 Turbo Preview (유료)',

      legacyModels: '이전 모델',
      gpt4: 'GPT-4 (유료)',
      gpt40613: 'GPT-4 (0613) (유료)',

      openaiHint: '💡 GPT-4o Mini가 가격 대비 성능이 좋아 추천됩니다. o1은 복잡한 추론 작업에 적합합니다.',

      geminiModel: 'Gemini 모델',
      gemini3: 'Gemini 3 (최신 Preview) 🚀',
      gemini3ProPreview: 'Gemini 3 Pro Preview (고성능)',
      gemini25: 'Gemini 2.5 (안정 버전) ⭐ 추천',
      gemini25Flash: 'Gemini 2.5 Flash (무료 - 안정)',
      gemini25Pro: 'Gemini 2.5 Pro (무료 - 고성능)',
      gemini25FlashLite: 'Gemini 2.5 Flash Lite (경량)',
      previousVersions: '이전 버전',
      gemini20FlashLite: 'Gemini 2.0 Flash Lite (경량)',

      geminiHint: '💡 Gemini 2.5 Flash가 안정적이며 할당량이 넉넉합니다. (추천)',
      geminiWarning: '⚠️ 무료 할당량 초과 시 429 에러가 발생할 수 있습니다.',

      geminiApiKey: 'Gemini API 키',
      geminiApiKeyFrom: 'Gemini API 키는',
      openaiApiKey: 'OpenAI API 키',
      openaiApiKeyFrom: 'OpenAI API 키는',
      apiKeyFrom: '에서 발급받을 수 있습니다.',
      apiKeyFromSuffix: '에서 발급받을 수 있습니다.',

      pricing: {
        title: '💰 요금 정보',
        openai: 'OpenAI (모두 유료):',
        o1: 'o1: $15/1M 입력, $60/1M 출력 (고급 추론)',
        gpt4oMini: 'GPT-4o Mini: $0.15/1M 입력, $0.60/1M 출력 (가장 저렴, 추천)',
        gpt4o: 'GPT-4o: $2.50/1M 입력, $10.00/1M 출력',
        gpt4Turbo: 'GPT-4 Turbo: $10/1M 입력, $30/1M 출력',
        gpt4: 'GPT-4: $30/1M 입력, $60/1M 출력',
        gemini: 'Gemini (무료 할당량 제공 ⭐):',
        free: '무료 할당량: 분당 15회, 일일 1,500회',
        gemini3: 'Gemini 3.0 Flash Exp: 무료 (최신)',
        gemini25: 'Gemini 2.5 Flash Exp: 무료 (안정적, 추천)',
        gemini25Pro: 'Gemini 2.5 Pro Exp: 무료 (고성능)'
      }
    },

    googleSearch: {
      title: '🔍 Google Custom Search API 설정',
      description: '이미지 검색 기능을 사용하려면 Google Custom Search API 키와 Search Engine ID가 필요합니다.',
      apiKey: 'Google Custom Search API 키',
      apiKeyHint: 'Google Cloud Console에서 Custom Search JSON API를 활성화하고 API 키를 발급받으세요.',
      getApiKey: 'API 키 발급받기 →',
      searchEngineId: 'Search Engine ID',
      searchEngineIdHint: '(cx 파라미터)',
      searchEngineIdDescription: 'Programmable Search Engine에서 이미지 검색을 활성화한 검색 엔진을 만들고 ID를 복사하세요.',
      createSearchEngine: 'Search Engine 만들기 →',

      guide: {
        title: '💡 설정 가이드',
        step1: '1. API 키 발급:',
        step1: {
          item1: 'Google Cloud Console → API 및 서비스 → 사용자 인증 정보',
          item2: '\'Custom Search JSON API\' 활성화',
          item3: 'API 키 생성'
        },
        step2: '2. Search Engine 생성:',
        step2: {
          item1: 'Programmable Search Engine 페이지 접속',
          item2: '새 검색 엔진 만들기 (전체 웹 검색)',
          item3: '\'이미지 검색\' 활성화',
          item4: '검색 엔진 ID 복사 (cx 파라미터)'
        }
      },

      freeQuota: '무료 할당량:',
      freeQuotaDetails: '일일 100회 검색 가능'
    },

    customPrompt: {
      title: '📝 커스텀 프롬프트',
      description: 'AI에게 질문할 프롬프트를 커스터마이징할 수 있습니다',
      variables: '💡 사용 가능한 변수:',
      softwareName: '{software_name}',
      softwareNameDesc: '- 소프트웨어 이름으로 자동 치환됩니다',
      tip: '팁: 더 상세하고 구체적인 질문을 하면 AI가 더 정확한 정보를 제공합니다.',
      openai: 'OpenAI 프롬프트',
      gemini: 'Gemini 프롬프트',
      restoreDefault: '기본값으로 복원',
      charCount: '현재 문자 수:',
      enableHint: '커스텀 프롬프트를 사용하려면 위의 \'사용\' 체크박스를 선택하세요.',

      placeholder: {
        openai: 'OpenAI에게 질문할 프롬프트를 입력하세요...',
        gemini: 'Gemini에게 질문할 프롬프트를 입력하세요...'
      }
    },

    scanExceptions: {
      title: '🚫 스캔 예외 설정',
      description: '스캔에서 제외할 파일 및 폴더를 설정합니다',
      files: '📄 파일 패턴',
      filesHint: '제외할 파일 패턴을 입력하세요. 와일드카드 (*) 사용 가능합니다.',
      filesPlaceholder: '예: *.txt, *.log, Thumbs.db'
    }
  },

  // ============================================
  // 관리자 (Admin)
  // ============================================
  admin: {
    title: '시스템 관리',
    description: '파일 스캔 및 스케줄러 설정',
    scanPrograms: '프로그램 스캔하기',

    tabs: {
      manualScan: '수동 스캔',
      scheduler: '자동 스캔 스케줄러',
      unmatched: '불일치 목록'
    },

    manualScan: {
      title: '수동 파일 스캔',
      useAI: 'AI 메타데이터 생성 활성화 (OpenAI API 필요)',
      benefit1: '✓ 정확한 프로그램 이름, 설명, 제조사 자동 생성',
      benefit2: '✓ 적절한 카테고리 자동 분류',
      benefit3: '✓ 공식 아이콘 이미지 다운로드 및 캐싱',
      pathPlaceholder: '/mnt/software',
      start: '스캔 시작',
      scanning: '스캔 중...',
      complete: '✓ 스캔 완료',
      newProducts: '새로운 프로그램:',
      count: '개',
      newVersions: '새로운 버전:',
      updatedProducts: '업데이트된 프로그램:',
      aiGenerated: 'AI 메타데이터 생성:',
      iconsCached: '아이콘 캐싱:',
      errors: '에러:',
      errorDetails: '에러 상세보기'
    },

    unmatched: {
      stats: {
        total: '전체',
        pending: '대기중',
        approved: '승인됨',
        manual: '수동입력',
        ignored: '무시됨'
      },

      filter: {
        label: '상태 필터:',
        all: '전체',
        pending: '대기중',
        approved: '승인됨',
        manual: '수동입력',
        ignored: '무시됨'
      },

      table: {
        filename: '파일명',
        parsedName: '파싱명',
        confidence: '정확도',
        aiSuggestion: 'AI 제안'
      },

      status: {
        pending: '대기중',
        approved: '승인됨',
        manual: '수동입력',
        ignored: '무시됨'
      },

      noItemsFiltered: '해당 상태의 항목이 없습니다.',
      noItems: '불일치 항목이 없습니다.',
      hint: '스캔 시 정확도 90% 미만인 항목이 여기에 표시됩니다.'
    },

    info: {
      title: '시스템 정보',
      phase: '🚀 Phase 2 기능 활성화됨',
      parsingAlgorithm: '파일명 파싱 알고리즘',
      parsingAlgorithmDesc: '파일명에서 소프트웨어 이름, 버전, 제조사 자동 추출',
      aiMetadata: 'AI 메타데이터 생성',
      aiMetadataDesc: 'OpenAI GPT를 사용하여 정확한 설명, 제조사, 카테고리 생성',
      iconCaching: '아이콘 다운로드 및 캐싱',
      iconCachingDesc: '공식 아이콘을 자동으로 찾아서 로컬에 캐쉬',
      fallback: 'Fallback 메커니즘',
      fallbackDesc: 'AI API 키가 없거나 오류 발생 시 파싱 정보로 자동 대체',

      tips: '💡 사용 팁',
      tipSetupOpenAI: 'OpenAI API 키를 설정하려면',
      tipSetupOpenAISuffix: '파일에서 OPENAI_API_KEY를 설정하세요',
      tipWithoutAI: 'AI 기능 없이도 기본 메타데이터로 동작합니다',
      tipFolderName: '폴더명이 명확할수록 더 정확한 메타데이터가 생성됩니다'
    }
  },

  // ============================================
  // 카테고리 (Categories)
  // ============================================
  category: {
    Graphics: '그래픽',
    Office: '오피스',
    Development: '개발',
    Utility: '유틸리티',
    Media: '미디어',
    OS: '운영체제',
    Security: '보안',
    Network: '네트워크',
    Mac: 'Mac',
    Mobile: '모바일',
    Patch: '패치',
    Driver: '드라이버',
    Source: '소스',
    Backup: '백업',
    Business: '비즈니스',
    Engineering: '엔지니어링',
    Theme: '테마',
    Hardware: '하드웨어',
    Uncategorized: '미분류'
  },

  // ============================================
  // 즐겨찾기 (Favorites)
  // ============================================
  favorites: {
    title: '❤️ 즐겨찾기',
    description: '내가 즐겨찾기한 프로그램 목록입니다',
    remove: '즐겨찾기 해제',
    goToStore: '스토어로 이동',

    empty: {
      title: '즐겨찾기가 비어있습니다',
      description: '스토어에서 마음에 드는 프로그램을 즐겨찾기에 추가해보세요'
    }
  },

  // ============================================
  // 스크랩 (Scraps)
  // ============================================
  scraps: {
    title: '📌 스크랩',
    description: '내가 스크랩한 팁&테크 게시글 목록입니다',
    goToTips: '팁&테크로 이동',

    table: {
      scrapDate: '스크랩 날짜'
    },

    empty: {
      title: '스크랩이 비어있습니다',
      description: '팁&테크 게시판에서 유용한 글을 스크랩해보세요'
    }
  },

  // ============================================
  // 비밀번호 변경 (Change Password)
  // ============================================
  changePassword: {
    title: '비밀번호 변경',
    description: '보안을 위해 주기적으로 비밀번호를 변경해주세요',
    submit: '비밀번호 변경',
    submitting: '변경 중...',
    warning: '비밀번호를 변경하면 모든 디바이스에서 자동으로 로그아웃됩니다. 새로운 비밀번호로 다시 로그인해야 합니다.',

    form: {
      currentPassword: '현재 비밀번호 *',
      currentPasswordPlaceholder: '현재 비밀번호를 입력하세요',
      newPassword: '새 비밀번호 *',
      newPasswordPlaceholder: '새 비밀번호를 입력하세요 (최소 4자)',
      minLengthHint: '비밀번호는 최소 4자 이상이어야 합니다',
      confirmPassword: '새 비밀번호 확인 *',
      confirmPasswordPlaceholder: '새 비밀번호를 다시 입력하세요'
    },

    validation: {
      mismatch: '새 비밀번호가 일치하지 않습니다.',
      minLength: '비밀번호는 최소 4자 이상이어야 합니다.',
      same: '현재 비밀번호와 새 비밀번호가 동일합니다.'
    },

    success: {
      changed: '비밀번호가 성공적으로 변경되었습니다.'
    },

    error: {
      wrongPassword: '현재 비밀번호가 올바르지 않습니다.',
      failed: '비밀번호 변경에 실패했습니다. 다시 시도해주세요.'
    },

    guide: {
      title: '비밀번호 보안 팁',
      tip1: '추측하기 어려운 비밀번호를 사용하세요',
      tip2: '다른 서비스와 다른 비밀번호를 사용하세요',
      tip3: '주기적으로 비밀번호를 변경하세요'
    }
  },

  // ============================================
  // 검색된 목록 (Filename Violations)
  // ============================================
  filenameViolations: {
    title: '검색된 목록',
    subtitle: '스캔된 파일 목록입니다',

    // 통계
    stats: {
      total: '전체 항목',
      scanned: '스캔된 항목',
      mismatched: '불일치 항목'
    },

    // 액션 버튼
    actions: {
      selectAll: '전체 선택',
      deselectAll: '전체 해제',
      batchRename: '선택 항목 일괄 변경',
      refresh: '새로고침',
      applySuggestion: '제안으로 변경',
      editFilename: '파일명 수정',
      markResolved: '해결됨으로 표시',
      delete: '삭제',
      aiMatching: 'AI 메타데이터 생성'
    },

    // 위반 유형
    violationType: {
      underscore_overuse: '언더스코어 과다',
      bracket_usage: '대괄호 사용',
      version_format: '버전 형식 오류',
      lowercase_name: '소문자 전용',
      complex_name: '파일명 복잡',
      invalid_chars: '특수문자 사용'
    },

    // 편집 모드
    editing: {
      title: '파일명 수정 중',
      placeholder: '새로운 파일명을 입력하세요',
      save: '저장',
      cancel: '취소'
    },

    // 메시지
    messages: {
      noViolations: '검색된 파일이 없습니다',
      allMatching: '스캔된 파일이 없습니다',
      renameSuccess: '파일명이 성공적으로 변경되었습니다.\nAI 매칭 버튼을 클릭하여 메타데이터를 업데이트할 수 있습니다.',
      renameConfirm: '로 변경하시겠습니까?',
      batchRenameConfirm: '선택한 {{count}}개 항목을 제안된 파일명으로 변경하시겠습니까?',
      deleteConfirm: '이 항목을 삭제하시겠습니까?',
      aiMatchingConfirm: 'AI로 메타데이터를 재생성하시겠습니까?',
      aiMatchingSuccess: '메타데이터가 성공적으로 업데이트되었습니다.\n스토어 페이지로 이동합니다.',
      selectItemsFirst: '변경할 항목을 선택해주세요.',
      noSuggestion: '제안된 파일명이 없습니다.',
      enterFilename: '파일명을 입력해주세요.',
      productIdNotFound: 'Product ID를 찾을 수 없습니다.',
      batchRenameHint: '\n\nAI 매칭 버튼을 클릭하여 메타데이터를 업데이트할 수 있습니다.'
    },

    // 항목 정보
    item: {
      problem: '문제:',
      suggestion: '제안:',
      discoveredAt: '발견 시각:'
    }
  },

  // ============================================
  // 푸터 (Footer)
  // ============================================
  footer: {
    copyright: 'All rights reserved.',
    subtitle: '개인용 소프트웨어 라이브러리 관리 시스템'
  }
}
