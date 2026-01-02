<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-8 py-4">
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
      <div class="px-8 pt-8 pb-6 max-w-5xl mx-auto">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">📋 정규식 안내</h1>
        <p class="text-gray-600 dark:text-gray-400">MyApp Store 파일 및 폴더 이름 표준 가이드</p>
      </div>

      <div class="px-8 pb-8">
        <div class="max-w-5xl mx-auto space-y-8">
          <!-- 표준 형식 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
            <span class="mr-2">📐</span>
            표준 형식
          </h2>

          <div class="space-y-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">기본 형식 (버전 있음)</h3>
              <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 font-mono text-sm">
                <code class="text-blue-600 dark:text-blue-400">제품명.v버전-기타내용.확장자</code>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">버전 없는 경우</h3>
              <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 font-mono text-sm">
                <code class="text-blue-600 dark:text-blue-400">제품명-기타내용.확장자</code>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">최소 형식</h3>
              <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 font-mono text-sm space-y-1">
                <div><code class="text-blue-600 dark:text-blue-400">제품명.v버전.확장자</code></div>
                <div><code class="text-blue-600 dark:text-blue-400">제품명.확장자</code></div>
              </div>
            </div>

            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6 border border-blue-200 dark:border-blue-800">
              <h3 class="text-lg font-semibold text-blue-800 dark:text-blue-300 mb-3 flex items-center">
                <span class="mr-2">💡</span>
                포터블/설치형 구분
              </h3>
              <div class="space-y-3 text-sm text-gray-700 dark:text-gray-300">
                <p><strong class="text-blue-700 dark:text-blue-400">포터블(Portable) 판별 규칙:</strong></p>
                <ul class="list-disc list-inside ml-4 space-y-1">
                  <li>파일명에 <code class="bg-white dark:bg-gray-800 px-2 py-0.5 rounded text-blue-600 dark:text-blue-400">Portable</code> 또는 <code class="bg-white dark:bg-gray-800 px-2 py-0.5 rounded text-blue-600 dark:text-blue-400">무설치</code> 키워드가 포함된 경우</li>
                  <li>대소문자 구분 없음 (portable, PORTABLE, Portable 모두 인식)</li>
                  <li>제품 상세 페이지에 "포터블" 또는 "설치형" 뱃지로 표시됨</li>
                </ul>
                <p class="mt-3"><strong class="text-blue-700 dark:text-blue-400">예시:</strong></p>
                <div class="space-y-1 ml-4">
                  <div class="bg-white dark:bg-gray-800 rounded p-2 font-mono text-xs">
                    <span class="text-green-600 dark:text-green-400">✓</span> Total Commander.v10.51-Portable.zip
                  </div>
                  <div class="bg-white dark:bg-gray-800 rounded p-2 font-mono text-xs">
                    <span class="text-green-600 dark:text-green-400">✓</span> Adobe Photoshop.v2024-무설치.exe
                  </div>
                  <div class="bg-white dark:bg-gray-800 rounded p-2 font-mono text-xs">
                    <span class="text-green-600 dark:text-green-400">✓</span> 7-Zip-Portable Korean.exe
                  </div>
                </div>
              </div>
            </div>
          </div>
          </div>

          <!-- 올바른 예시 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
            <span class="mr-2">✅</span>
            올바른 예시
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-sm font-semibold text-green-600 dark:text-green-400 mb-3">패턴 1: 완전한 정보</h3>
              <div class="space-y-2">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                  Total Commander.v10.51-Final.zip
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                  ACDSee Photo Studio.v2024-Ultimate.exe
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-sm font-semibold text-green-600 dark:text-green-400 mb-3">패턴 2: 버전 없음</h3>
              <div class="space-y-2">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                  Adobe Photoshop-Portable.exe
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                  Total Commander-Korean.zip
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-sm font-semibold text-green-600 dark:text-green-400 mb-3">패턴 3: 기본 정보만</h3>
              <div class="space-y-2">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                  Acronis True Image.v2019.exe
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                  Microsoft Office.v2021.iso
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-sm font-semibold text-green-600 dark:text-green-400 mb-3">패턴 4: 제품명만</h3>
              <div class="space-y-2">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                  VLC Media Player.exe
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                  Notepad++.zip
                </div>
              </div>
            </div>
          </div>
          </div>

          <!-- 피해야 할 형식 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
            <span class="mr-2">❌</span>
            피해야 할 형식
          </h2>

          <div class="space-y-4">
            <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4">
              <div class="font-mono text-sm text-gray-800 dark:text-gray-200 mb-2">
                Total_Commander_10.51_Final_with_Key_x64.zip
              </div>
              <p class="text-sm text-red-700 dark:text-red-400">→ 너무 복잡하고 언더스코어 과다 사용</p>
            </div>

            <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4">
              <div class="font-mono text-sm text-gray-800 dark:text-gray-200 mb-2">
                TCMDv1051.zip
              </div>
              <p class="text-sm text-red-700 dark:text-red-400">→ 제품명이 불분명함</p>
            </div>

            <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4">
              <div class="font-mono text-sm text-gray-800 dark:text-gray-200 mb-2">
                total-commander-v10-51-final.zip
              </div>
              <p class="text-sm text-red-700 dark:text-red-400">→ 소문자, 버전 구분자 혼란</p>
            </div>

            <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4">
              <div class="font-mono text-sm text-gray-800 dark:text-gray-200 mb-2">
                [Total Commander] v10.51 - Final.zip
              </div>
              <p class="text-sm text-red-700 dark:text-red-400">→ 대괄호 입력 불편</p>
            </div>
          </div>
          </div>

          <!-- 세부 규칙 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
            <span class="mr-2">📐</span>
            세부 규칙
          </h2>

          <div class="space-y-6">
            <!-- 제품명 -->
            <div>
              <h3 class="text-lg font-semibold text-indigo-600 dark:text-indigo-400 mb-3">1. 제품명 (Product Name)</h3>
              <ul class="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                <li><strong>공식 제품명</strong> 사용 (대소문자 구분)</li>
                <li>띄어쓰기 포함 가능</li>
                <li>특수문자는 피하기 (<code>.</code> <code>-</code> 제외)</li>
              </ul>
              <div class="mt-3 grid grid-cols-2 gap-3">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                  <code class="text-sm text-gray-800 dark:text-gray-200">Total Commander</code>
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                  <code class="text-sm text-gray-800 dark:text-gray-200">Adobe Photoshop CC</code>
                </div>
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                  <span class="text-red-600 dark:text-red-400 mr-2">❌</span>
                  <code class="text-sm text-gray-800 dark:text-gray-200">Total_Commander</code>
                </div>
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                  <span class="text-red-600 dark:text-red-400 mr-2">❌</span>
                  <code class="text-sm text-gray-800 dark:text-gray-200">TotalCommander</code>
                </div>
              </div>
            </div>

            <!-- 버전 -->
            <div>
              <h3 class="text-lg font-semibold text-indigo-600 dark:text-indigo-400 mb-3">2. 버전 (Version)</h3>
              <ul class="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                <li><code>.v</code> 접두사 사용 (필수)</li>
                <li>숫자와 점(<code>.</code>)만 사용</li>
                <li>연도도 버전으로 간주 (2023, 2024 등)</li>
              </ul>
              <div class="mt-3 grid grid-cols-2 gap-3">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                  <code class="text-sm text-gray-800 dark:text-gray-200">.v10.51</code>
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                  <code class="text-sm text-gray-800 dark:text-gray-200">.v2024</code>
                </div>
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                  <span class="text-red-600 dark:text-red-400 mr-2">❌</span>
                  <code class="text-sm text-gray-800 dark:text-gray-200">.10.51</code>
                  <span class="text-xs text-red-600 dark:text-red-400"> (v 누락)</span>
                </div>
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                  <span class="text-red-600 dark:text-red-400 mr-2">❌</span>
                  <code class="text-sm text-gray-800 dark:text-gray-200">.vBuild14110</code>
                  <span class="text-xs text-red-600 dark:text-red-400"> (숫자가 아님)</span>
                </div>
              </div>
            </div>

            <!-- 기타내용 -->
            <div>
              <h3 class="text-lg font-semibold text-indigo-600 dark:text-indigo-400 mb-3">3. 기타내용 (Description)</h3>
              <ul class="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                <li><code>-</code> 구분자 사용</li>
                <li>간단명료하게</li>
                <li>여러 정보는 쉼표 또는 띄어쓰기로 구분</li>
              </ul>
              <div class="mt-3 grid grid-cols-2 gap-3">
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                  <code class="text-sm text-gray-800 dark:text-gray-200">-Final</code>
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                  <code class="text-sm text-gray-800 dark:text-gray-200">-Portable</code>
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                  <code class="text-sm text-gray-800 dark:text-gray-200">-Multilingual</code>
                </div>
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                  <span class="text-red-600 dark:text-red-400 mr-2">❌</span>
                  <code class="text-sm text-gray-800 dark:text-gray-200">-Final_with_Key</code>
                </div>
              </div>
            </div>
          </div>
          </div>

          <!-- 특수 카테고리 자동 인식 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
            <span class="mr-2">🏷️</span>
            특수 카테고리 자동 인식
          </h2>

          <div class="space-y-6">
            <!-- Portable 규칙 -->
            <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-purple-700 dark:text-purple-300 mb-4 flex items-center">
                <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Portable (포터블) 프로그램
              </h3>

              <div class="space-y-4">
                <div>
                  <p class="text-gray-700 dark:text-gray-300 mb-3">
                    파일명이나 폴더명에 <code class="bg-white dark:bg-gray-800 px-2 py-1 rounded text-purple-600 dark:text-purple-400 font-semibold">Portable</code> 키워드가 포함되면 자동으로 <strong>"Portable"</strong> 카테고리로 분류됩니다.
                  </p>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    <div>
                      <p class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">파일명 예시:</p>
                      <div class="space-y-2">
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                          <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                          <code class="text-sm text-gray-800 dark:text-gray-200">Adobe Photoshop-Portable.exe</code>
                        </div>
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                          <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                          <code class="text-sm text-gray-800 dark:text-gray-200">VLC Media Player.v3.0-Portable.zip</code>
                        </div>
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                          <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                          <code class="text-sm text-gray-800 dark:text-gray-200">Notepad++ Portable.v8.5.exe</code>
                        </div>
                      </div>
                    </div>

                    <div>
                      <p class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">폴더명 예시:</p>
                      <div class="space-y-2">
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                          <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                          <code class="text-sm text-gray-800 dark:text-gray-200">Adobe Photoshop Portable/</code>
                        </div>
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                          <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                          <code class="text-sm text-gray-800 dark:text-gray-200">Total Commander-Portable/</code>
                        </div>
                        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                          <span class="text-green-600 dark:text-green-400 mr-2">✅</span>
                          <code class="text-sm text-gray-800 dark:text-gray-200">PortableApps/</code>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500 p-4 mt-4">
                  <div class="flex">
                    <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div class="text-sm text-blue-700 dark:text-blue-300">
                      <p class="font-semibold mb-1">💡 자동 인식 규칙</p>
                      <ul class="list-disc list-inside space-y-1 ml-2">
                        <li>대소문자 구분 없음 (portable, Portable, PORTABLE 모두 인식)</li>
                        <li>파일명과 폴더명 모두 적용</li>
                        <li>AI 스캔 시 자동으로 "Portable" 카테고리로 분류</li>
                        <li>설치가 필요 없는 실행 파일 형식에 권장</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div class="mt-4">
                  <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">권장 파일명 형식:</p>
                  <div class="space-y-2">
                    <div class="flex items-center space-x-2">
                      <code class="bg-white dark:bg-gray-800 px-3 py-2 rounded text-sm text-gray-800 dark:text-gray-200 flex-1 font-mono">
                        제품명-Portable.확장자
                      </code>
                      <span class="text-xs text-gray-500 dark:text-gray-400">(버전 없음)</span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <code class="bg-white dark:bg-gray-800 px-3 py-2 rounded text-sm text-gray-800 dark:text-gray-200 flex-1 font-mono">
                        제품명.v버전-Portable.확장자
                      </code>
                      <span class="text-xs text-gray-500 dark:text-gray-400">(버전 있음)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 향후 추가 가능한 특수 카테고리 안내 -->
            <div class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <p class="text-sm text-gray-600 dark:text-gray-400">
                <strong>참고:</strong> 향후 Patch, Crack, Keygen 등 다른 특수 카테고리에 대한 자동 인식 규칙이 추가될 수 있습니다.
              </p>
            </div>
          </div>
          </div>

          <!-- 변환 예시 -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 border border-gray-100 dark:border-gray-700">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
            <span class="mr-2">📊</span>
            변환 예시
          </h2>

          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">기존 파일명</th>
                  <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">표준 형식</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr>
                  <td class="px-4 py-3 font-mono text-sm text-gray-600 dark:text-gray-400">Total_Commander_10.51_Final.zip</td>
                  <td class="px-4 py-3 font-mono text-sm text-green-600 dark:text-green-400 font-semibold">Total Commander.v10.51-Final.zip</td>
                </tr>
                <tr>
                  <td class="px-4 py-3 font-mono text-sm text-gray-600 dark:text-gray-400">ACDSee_2024_Ultimate.exe</td>
                  <td class="px-4 py-3 font-mono text-sm text-green-600 dark:text-green-400 font-semibold">ACDSee Photo Studio.v2024-Ultimate.exe</td>
                </tr>
                <tr>
                  <td class="px-4 py-3 font-mono text-sm text-gray-600 dark:text-gray-400">adobe_photoshop_cc_2023_portable.zip</td>
                  <td class="px-4 py-3 font-mono text-sm text-green-600 dark:text-green-400 font-semibold">Adobe Photoshop CC.v2023-Portable.zip</td>
                </tr>
                <tr>
                  <td class="px-4 py-3 font-mono text-sm text-gray-600 dark:text-gray-400">vlc-media-player-portable.exe</td>
                  <td class="px-4 py-3 font-mono text-sm text-green-600 dark:text-green-400 font-semibold">VLC Media Player-Portable.exe</td>
                </tr>
              </tbody>
            </table>
          </div>
          </div>

          <!-- 체크리스트 -->
          <div class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-2xl shadow-sm p-8 border border-blue-200 dark:border-blue-700">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
            <span class="mr-2">📝</span>
            파일 업로드 전 체크리스트
          </h2>

          <div class="space-y-3">
            <div class="flex items-start space-x-3">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-gray-700 dark:text-gray-300">제품명이 공식 명칭인가?</span>
            </div>
            <div class="flex items-start space-x-3">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-gray-700 dark:text-gray-300">버전이 있다면 <code class="bg-white dark:bg-gray-800 px-2 py-1 rounded">.v</code> 형식인가?</span>
            </div>
            <div class="flex items-start space-x-3">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-gray-700 dark:text-gray-300">기타내용이 있다면 <code class="bg-white dark:bg-gray-800 px-2 py-1 rounded">-</code>로 시작하는가?</span>
            </div>
            <div class="flex items-start space-x-3">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-gray-700 dark:text-gray-300">언더스코어(<code class="bg-white dark:bg-gray-800 px-2 py-1 rounded">_</code>)를 띄어쓰기로 변경했는가?</span>
            </div>
            <div class="flex items-start space-x-3">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-gray-700 dark:text-gray-300">확장자가 소문자인가?</span>
            </div>
            <div class="flex items-start space-x-3">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-gray-700 dark:text-gray-300">파일명이 간결한가? (불필요한 정보 제거)</span>
            </div>
          </div>
          </div>

          <!-- 빠른 참조 -->
          <div class="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-2xl shadow-sm p-8 border border-purple-200 dark:border-purple-700">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
            <span class="mr-2">📌</span>
            빠른 참조
          </h2>

          <div class="space-y-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">완전한 형식:</p>
                  <code class="text-blue-600 dark:text-blue-400 font-mono">제품명.v버전-기타내용.확장자</code>
                </div>
                <div>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">버전 없음:</p>
                  <code class="text-blue-600 dark:text-blue-400 font-mono">제품명-기타내용.확장자</code>
                </div>
                <div>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">기본 형식:</p>
                  <code class="text-blue-600 dark:text-blue-400 font-mono">제품명.v버전.확장자</code>
                </div>
                <div>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">최소 형식:</p>
                  <code class="text-blue-600 dark:text-blue-400 font-mono">제품명.확장자</code>
                </div>
              </div>
            </div>

            <div class="space-y-2">
              <p class="text-sm font-semibold text-gray-700 dark:text-gray-300">예시:</p>
              <div class="space-y-2">
                <div class="flex items-center space-x-2">
                  <span class="text-green-600 dark:text-green-400">✅</span>
                  <code class="font-mono text-sm text-gray-800 dark:text-gray-200">Total Commander.v10.51-Final.zip</code>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-green-600 dark:text-green-400">✅</span>
                  <code class="font-mono text-sm text-gray-800 dark:text-gray-200">ACDSee Photo Studio.v2024-Ultimate.exe</code>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-green-600 dark:text-green-400">✅</span>
                  <code class="font-mono text-sm text-gray-800 dark:text-gray-200">Adobe Photoshop-Portable.exe</code>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-green-600 dark:text-green-400">✅</span>
                  <code class="font-mono text-sm text-gray-800 dark:text-gray-200">Notepad++.exe</code>
                </div>
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// This is a static page, no logic needed
</script>
