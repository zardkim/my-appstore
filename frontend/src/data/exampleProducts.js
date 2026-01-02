// 예제 프로그램 데이터
export const exampleProducts = [
  {
    id: 1,
    title: 'Adobe Photoshop 2024',
    vendor: 'Adobe Inc.',
    category: 'Graphics',
    description: '전문가를 위한 이미지 편집 및 디자인 소프트웨어입니다. 사진 편집, 합성, 디지털 페인팅 등 다양한 기능을 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/5968/5968520.png',
    versions: [
      {
        id: 1,
        version_name: '2024 v25.0',
        file_name: 'Adobe_Photoshop_2024_v25.0.exe',
        file_size: 3221225472, // 3GB
        release_date: '2024-01-15'
      },
      {
        id: 2,
        version_name: '2023 v24.5',
        file_name: 'Adobe_Photoshop_2023_v24.5.exe',
        file_size: 2952790016, // 2.75GB
        release_date: '2023-08-20'
      }
    ]
  },
  {
    id: 2,
    title: 'Microsoft Office 365',
    vendor: 'Microsoft Corporation',
    category: 'Office',
    description: '워드, 엑셀, 파워포인트 등을 포함한 오피스 생산성 도구 모음입니다. 클라우드 기반 협업 기능을 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/732/732221.png',
    versions: [
      {
        id: 3,
        version_name: '2024 Professional Plus',
        file_name: 'Office_365_2024_ProPlus.iso',
        file_size: 4294967296, // 4GB
        release_date: '2024-02-01'
      }
    ]
  },
  {
    id: 3,
    title: 'Visual Studio Code',
    vendor: 'Microsoft Corporation',
    category: 'Development',
    description: '강력하고 가벼운 코드 편집기입니다. 다양한 프로그래밍 언어를 지원하며, 풍부한 확장 기능을 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/906/906324.png',
    versions: [
      {
        id: 4,
        version_name: '1.85.1',
        file_name: 'VSCode_1.85.1_x64.exe',
        file_size: 94371840, // 90MB
        release_date: '2024-01-10'
      },
      {
        id: 5,
        version_name: '1.84.2',
        file_name: 'VSCode_1.84.2_x64.exe',
        file_size: 93323264, // 89MB
        release_date: '2023-12-15'
      }
    ]
  },
  {
    id: 4,
    title: 'WinRAR',
    vendor: 'RARLAB',
    category: 'Utility',
    description: '강력한 압축 프로그램입니다. RAR, ZIP 등 다양한 압축 형식을 지원하며, 파일 분할 및 암호화 기능을 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/337/337946.png',
    versions: [
      {
        id: 6,
        version_name: '6.24',
        file_name: 'winrar-x64-624.exe',
        file_size: 3145728, // 3MB
        release_date: '2024-01-05'
      }
    ]
  },
  {
    id: 5,
    title: 'VLC Media Player',
    vendor: 'VideoLAN',
    category: 'Media',
    description: '무료 오픈소스 미디어 플레이어입니다. 거의 모든 비디오 및 오디오 형식을 재생할 수 있습니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/732/732192.png',
    versions: [
      {
        id: 7,
        version_name: '3.0.20',
        file_name: 'vlc-3.0.20-win64.exe',
        file_size: 41943040, // 40MB
        release_date: '2024-01-20'
      }
    ]
  },
  {
    id: 6,
    title: 'Google Chrome',
    vendor: 'Google LLC',
    category: 'Network',
    description: '빠르고 안전한 웹 브라우저입니다. 다양한 확장 프로그램과 동기화 기능을 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/732/732221.png',
    versions: [
      {
        id: 8,
        version_name: '120.0.6099',
        file_name: 'ChromeSetup.exe',
        file_size: 104857600, // 100MB
        release_date: '2024-01-25'
      }
    ]
  },
  {
    id: 7,
    title: 'AutoCAD 2024',
    vendor: 'Autodesk',
    category: 'Graphics',
    description: '전문 CAD 소프트웨어입니다. 2D 및 3D 설계, 도면 작성, 모델링 기능을 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/2282/2282188.png',
    versions: [
      {
        id: 9,
        version_name: '2024.1',
        file_name: 'AutoCAD_2024_1.exe',
        file_size: 5368709120, // 5GB
        release_date: '2024-01-08'
      }
    ]
  },
  {
    id: 8,
    title: 'Slack',
    vendor: 'Slack Technologies',
    category: 'Office',
    description: '팀 협업을 위한 메신저 플랫폼입니다. 채널 기반 대화, 파일 공유, 앱 통합 기능을 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/2111/2111615.png',
    versions: [
      {
        id: 10,
        version_name: '4.36.140',
        file_name: 'slack-standalone-4.36.140.exe',
        file_size: 125829120, // 120MB
        release_date: '2024-01-18'
      }
    ]
  },
  {
    id: 9,
    title: 'Python 3.12',
    vendor: 'Python Software Foundation',
    category: 'Development',
    description: '강력하고 사용하기 쉬운 프로그래밍 언어입니다. 데이터 분석, 웹 개발, 자동화 등 다양한 용도로 사용됩니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/5968/5968350.png',
    versions: [
      {
        id: 11,
        version_name: '3.12.1',
        file_name: 'python-3.12.1-amd64.exe',
        file_size: 26214400, // 25MB
        release_date: '2023-12-08'
      }
    ]
  },
  {
    id: 10,
    title: 'CCleaner',
    vendor: 'Piriform',
    category: 'Utility',
    description: '시스템 최적화 및 정리 도구입니다. 불필요한 파일 삭제, 레지스트리 정리 등의 기능을 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/2702/2702134.png',
    versions: [
      {
        id: 12,
        version_name: '6.19',
        file_name: 'ccsetup619.exe',
        file_size: 52428800, // 50MB
        release_date: '2024-01-12'
      }
    ]
  },
  {
    id: 11,
    title: 'Spotify',
    vendor: 'Spotify AB',
    category: 'Media',
    description: '음악 스트리밍 서비스입니다. 수백만 곡의 음악과 팟캐스트를 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/174/174872.png',
    versions: [
      {
        id: 13,
        version_name: '1.2.28',
        file_name: 'SpotifySetup.exe',
        file_size: 146800640, // 140MB
        release_date: '2024-01-22'
      }
    ]
  },
  {
    id: 12,
    title: 'Malwarebytes',
    vendor: 'Malwarebytes Inc.',
    category: 'Security',
    description: '악성코드 및 바이러스 제거 도구입니다. 실시간 보호 및 정기적인 검사 기능을 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/2913/2913133.png',
    versions: [
      {
        id: 14,
        version_name: '4.6.7',
        file_name: 'MBSetup.exe',
        file_size: 83886080, // 80MB
        release_date: '2024-01-16'
      }
    ]
  },
  {
    id: 13,
    title: 'Steam',
    vendor: 'Valve Corporation',
    category: 'Utility',
    description: '게임 배포 플랫폼입니다. 수천 개의 게임을 구매하고 다운로드할 수 있으며, 커뮤니티 기능을 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/732/732234.png',
    versions: [
      {
        id: 15,
        version_name: '2024.01',
        file_name: 'SteamSetup.exe',
        file_size: 2097152, // 2MB
        release_date: '2024-01-20'
      }
    ]
  },
  {
    id: 14,
    title: 'FileZilla',
    vendor: 'Tim Kosse',
    category: 'Network',
    description: 'FTP 클라이언트 프로그램입니다. 파일 전송, 사이트 관리, 드래그 앤 드롭 기능을 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/9496/9496506.png',
    versions: [
      {
        id: 16,
        version_name: '3.66.4',
        file_name: 'FileZilla_3.66.4_win64-setup.exe',
        file_size: 14680064, // 14MB
        release_date: '2024-01-11'
      }
    ]
  },
  {
    id: 15,
    title: 'Windows 11 Pro',
    vendor: 'Microsoft Corporation',
    category: 'OS',
    description: '최신 Windows 운영체제입니다. 개선된 UI, 향상된 성능, 새로운 생산성 기능을 제공합니다.',
    icon_url: 'https://cdn-icons-png.flaticon.com/512/732/732221.png',
    versions: [
      {
        id: 17,
        version_name: '23H2',
        file_name: 'Win11_23H2_English_x64.iso',
        file_size: 6442450944, // 6GB
        release_date: '2023-10-31'
      }
    ]
  }
]

// 파일 크기를 사람이 읽기 쉬운 형식으로 변환
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

// 카테고리별 통계 계산
export const getCategoryStats = () => {
  const stats = {}
  exampleProducts.forEach(product => {
    if (stats[product.category]) {
      stats[product.category]++
    } else {
      stats[product.category] = 1
    }
  })
  return stats
}

// 최근 제품 가져오기
export const getRecentProducts = (limit = 12) => {
  return exampleProducts.slice(0, limit)
}

// 카테고리별 제품 필터링
export const filterByCategory = (category) => {
  if (!category) return exampleProducts
  return exampleProducts.filter(p => p.category === category)
}

// 검색
export const searchProducts = (query) => {
  if (!query) return exampleProducts
  const lowerQuery = query.toLowerCase()
  return exampleProducts.filter(p =>
    p.title.toLowerCase().includes(lowerQuery) ||
    p.vendor.toLowerCase().includes(lowerQuery) ||
    p.description.toLowerCase().includes(lowerQuery)
  )
}

// ID로 제품 찾기
export const getProductById = (id) => {
  return exampleProducts.find(p => p.id === parseInt(id))
}
