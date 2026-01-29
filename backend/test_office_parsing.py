#!/usr/bin/env python3
"""
MS Office 2021 LTSC와 MS Office 365 파싱 테스트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.parser import FilenameParser

def test_office_parsing():
    parser = FilenameParser()

    test_cases = [
        # 폴더명으로 테스트 (실제 스캔 시 폴더명이 사용됨)
        ("MS Office 2021 LTSC", ""),
        ("MS Office 365", ""),
        ("Microsoft Office 2021 Professional Plus", ""),
        ("Microsoft Office LTSC Professional Plus 2021", ""),
        ("Office 365 ProPlus", ""),

        # 파일명 + 폴더명으로 테스트
        ("setup.exe", "MS Office 2021 LTSC"),
        ("setup.exe", "MS Office 365"),

        # 복잡한 파일명
        ("Microsoft.Office.2021.LTSC.Professional.Plus.v2108.16.0.14332.20447.x64.iso", ""),
        ("Microsoft.Office.365.ProPlus.v2312.Build.17126.20132.x64.iso", ""),
    ]

    print("=" * 80)
    print("MS Office 파싱 테스트")
    print("=" * 80)

    for filename, parent_folder in test_cases:
        result = parser.parse(filename, parent_folder)

        print(f"\n입력:")
        print(f"  파일명: {filename}")
        if parent_folder:
            print(f"  폴더명: {parent_folder}")

        print(f"결과:")
        print(f"  소프트웨어명: {result['software_name']}")
        print(f"  버전: {result['version']}")
        print(f"  제조사: {result['vendor']}")
        print(f"  연도: {result['year']}")
        print(f"  포터블: {result['is_portable']}")
        print("-" * 80)

if __name__ == "__main__":
    test_office_parsing()
