<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 sm:px-8 py-4">
      <div class="flex items-center justify-between">
        <button
          @click="$router.back()"
          class="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          뒤로 가기
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
      <!-- Title Section -->
      <div class="px-4 sm:px-8 pt-6 sm:pt-8 pb-4 sm:pb-6 max-w-4xl mx-auto">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-2">🤖 AI 검색을 위한 파일명 가이드</h1>
        <p class="text-gray-600 dark:text-gray-400">AI가 제품 정보를 정확하게 인식할 수 있도록 파일명을 작성하는 방법을 안내합니다.</p>
      </div>

      <div class="px-4 sm:px-8 pb-8">
        <div class="max-w-4xl mx-auto space-y-6">

          <!-- AI 검색 원리 -->
          <div class="bg-blue-50 dark:bg-blue-900/20 rounded-2xl p-5 sm:p-8 border border-blue-200 dark:border-blue-700">
            <h2 class="text-xl sm:text-2xl font-bold text-blue-900 dark:text-blue-200 mb-4 flex items-center">
              <span class="mr-2">💡</span>
              왜 파일명이 중요한가요?
            </h2>
            <p class="text-blue-800 dark:text-blue-300 leading-relaxed">
              AI는 <strong>파일이 있는 폴더명</strong>을 기반으로 제품을 검색합니다.
              폴더명에 제품명이 명확하게 표기되어 있을수록 AI가 정확한 정보를 찾아올 수 있습니다.
              파일명은 파일명 규칙에 맞게 수정하면 AI 검색 결과가 좋아집니다.
            </p>
          </div>

          <!-- 폴더 구조 예시 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-5 sm:p-8 border border-gray-100 dark:border-gray-700">
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-5 flex items-center">
              <span class="mr-2">📁</span>
              권장 폴더 구조
            </h2>
            <div class="space-y-4">
              <p class="text-sm text-gray-600 dark:text-gray-400">스캔 폴더 안에 <strong>제품별 폴더</strong>를 만들고, 그 안에 파일을 넣으세요.</p>
              <div class="bg-gray-50 dark:bg-gray-900 rounded-xl p-4 font-mono text-sm space-y-1">
                <div class="text-gray-500 dark:text-gray-400">📂 스캔폴더/</div>
                <div class="ml-4 text-green-600 dark:text-green-400">📂 Adobe Photoshop/        ← 폴더명 = 제품명 (AI가 이 이름으로 검색)</div>
                <div class="ml-8 text-gray-700 dark:text-gray-300">📄 Adobe Photoshop.v2024.exe</div>
                <div class="ml-4 text-green-600 dark:text-green-400">📂 Microsoft Office/</div>
                <div class="ml-8 text-gray-700 dark:text-gray-300">📄 Microsoft Office.v2021.iso</div>
                <div class="ml-4 text-green-600 dark:text-green-400">📂 VLC Media Player/</div>
                <div class="ml-8 text-gray-700 dark:text-gray-300">📄 VLC Media Player.v3.0-Portable.zip</div>
              </div>
            </div>
          </div>

          <!-- 파일명 규칙 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-5 sm:p-8 border border-gray-100 dark:border-gray-700">
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-5 flex items-center">
              <span class="mr-2">📐</span>
              파일명 규칙
            </h2>
            <div class="space-y-5">
              <!-- 기본 형식 -->
              <div>
                <h3 class="text-base font-semibold text-gray-800 dark:text-gray-200 mb-3">기본 형식</h3>
                <div class="bg-gray-50 dark:bg-gray-900 rounded-xl p-4 font-mono text-sm space-y-2">
                  <div><code class="text-blue-600 dark:text-blue-400">제품명.v버전-기타.확장자</code> <span class="text-gray-500 ml-2">← 버전 있음</span></div>
                  <div><code class="text-blue-600 dark:text-blue-400">제품명-기타.확장자</code> <span class="text-gray-500 ml-2">← 버전 없음</span></div>
                  <div><code class="text-blue-600 dark:text-blue-400">제품명.확장자</code> <span class="text-gray-500 ml-2">← 최소 형식</span></div>
                </div>
              </div>

              <!-- 규칙 표 -->
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-xl p-4 border border-green-200 dark:border-green-800">
                  <p class="text-sm font-semibold text-green-700 dark:text-green-400 mb-2">제품명</p>
                  <ul class="text-xs text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• 공식 명칭 그대로 사용</li>
                    <li>• 대소문자 구분 유지</li>
                    <li>• 공백 사용 가능</li>
                    <li>• 특수문자는 <code>.</code> <code>-</code>만 허용</li>
                  </ul>
                </div>
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 border border-blue-200 dark:border-blue-800">
                  <p class="text-sm font-semibold text-blue-700 dark:text-blue-400 mb-2">버전 (.v 형식)</p>
                  <ul class="text-xs text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• <code>.v</code> 로 시작</li>
                    <li>• 숫자와 점만 사용</li>
                    <li>• 연도도 버전으로 가능</li>
                    <li>• 예: <code>.v10.51</code> <code>.v2024</code></li>
                  </ul>
                </div>
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 border border-purple-200 dark:border-purple-800">
                  <p class="text-sm font-semibold text-purple-700 dark:text-purple-400 mb-2">기타 정보 (- 형식)</p>
                  <ul class="text-xs text-gray-700 dark:text-gray-300 space-y-1">
                    <li>• <code>-</code> 로 시작</li>
                    <li>• Portable, Final 등</li>
                    <li>• 언어팩: Korean, Multi</li>
                    <li>• 아키텍처: x64, x86</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- 좋은 예 / 나쁜 예 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-5 sm:p-8 border border-gray-100 dark:border-gray-700">
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-5 flex items-center">
              <span class="mr-2">✅</span>
              올바른 파일명 예시
            </h2>
            <div class="space-y-2">
              <div v-for="item in goodExamples" :key="item.name" class="flex items-start gap-3 bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                <span class="text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5">✓</span>
                <div>
                  <code class="text-sm text-gray-800 dark:text-gray-200 font-mono">{{ item.name }}</code>
                  <span class="text-xs text-gray-500 dark:text-gray-400 ml-2">{{ item.desc }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 나쁜 예 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-5 sm:p-8 border border-gray-100 dark:border-gray-700">
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-5 flex items-center">
              <span class="mr-2">❌</span>
              AI가 인식하기 어려운 파일명
            </h2>
            <div class="space-y-3">
              <div v-for="item in badExamples" :key="item.name" class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-3 rounded-r-lg">
                <code class="text-sm text-gray-800 dark:text-gray-200 font-mono">{{ item.name }}</code>
                <p class="text-xs text-red-600 dark:text-red-400 mt-1">→ {{ item.reason }}</p>
              </div>
            </div>
          </div>

          <!-- 포터블 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-5 sm:p-8 border border-gray-100 dark:border-gray-700">
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-5 flex items-center">
              <span class="mr-2">🎒</span>
              포터블(Portable) 자동 인식
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">파일명 또는 폴더명에 <code class="bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded">Portable</code> 또는 <code class="bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded">무설치</code> 키워드가 포함되면 자동으로 포터블로 분류됩니다.</p>
            <div class="space-y-2">
              <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-sm">
                <span class="text-green-600 dark:text-green-400 mr-2">✓</span> Total Commander.v10.51-Portable.zip
              </div>
              <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-sm">
                <span class="text-green-600 dark:text-green-400 mr-2">✓</span> 폴더: Adobe Photoshop Portable/
              </div>
            </div>
          </div>

          <!-- 빠른 체크리스트 -->
          <div class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-2xl p-5 sm:p-8 border border-blue-200 dark:border-blue-700">
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-5 flex items-center">
              <span class="mr-2">📝</span>
              AI 검색 전 체크리스트
            </h2>
            <div class="space-y-3">
              <div v-for="check in checklist" :key="check" class="flex items-start gap-3">
                <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-gray-700 dark:text-gray-300 text-sm">{{ check }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const goodExamples = [
  { name: 'Adobe Photoshop.v2024.exe', desc: '제품명 + 버전 (연도)' },
  { name: 'Total Commander.v10.51-Final.zip', desc: '제품명 + 버전 + 기타' },
  { name: 'VLC Media Player.v3.0-Portable.zip', desc: '포터블 명시' },
  { name: 'Microsoft Office.v2021-x64.iso', desc: '아키텍처 명시' },
  { name: 'Notepad++.exe', desc: '최소 형식 (제품명만)' },
]

const badExamples = [
  { name: 'setup_final2.exe', desc: '제품명이 없어 AI가 무엇인지 알 수 없음' },
  { name: 'Total_Commander_10.51_Final_x64.zip', desc: '언더스코어 과다 사용, AI가 제품명을 파악하기 어려움' },
  { name: 'TCMDv1051.zip', desc: '약어 사용으로 제품명 불명확' },
  { name: 'aaa.exe', desc: '의미 없는 이름' },
  { name: '프로그램(1).exe', desc: '의미 없는 이름, 특수문자 포함' },
]

const checklist = [
  '폴더명이 공식 제품명과 동일한가? (AI는 폴더명으로 검색합니다)',
  '제품명에 불필요한 언더스코어(_)가 없는가?',
  '버전 정보가 있다면 .v 형식으로 작성했는가? (예: .v2024)',
  '파일명이 명확하게 제품을 식별할 수 있는가?',
  'AI 검색 결과가 좋지 않다면, 파일명 편집으로 수정 후 재시도',
]
</script>
