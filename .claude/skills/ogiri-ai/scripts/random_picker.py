#!/usr/bin/env python3
"""
ランダム選択スクリプト（シンプル版）

動的に生成された選択肢からランダムにn個選択します。
LLMの確率的偏りを排除し、真の意外性を導入します。

使用方法:
  python3 scripts/random_picker.py "選択肢1" "選択肢2" "選択肢3" [--n 個数]

例:
  python3 scripts/random_picker.py "朝礼" "校歌" "卒業式" "職員室" "教育方針"
  python3 scripts/random_picker.py "朝礼" "校歌" "卒業式" "職員室" "教育方針" --n 3
"""

import sys
import random


def pick_random(choices, n=1):
    """
    選択肢からランダムにn個選択する

    Args:
        choices: 選択肢のリスト
        n: 選択する個数（デフォルト1）

    Returns:
        選択結果のリスト
    """
    if not choices:
        raise ValueError("選択肢が空です")

    if n < 1:
        raise ValueError("n は1以上である必要があります")

    if n > len(choices):
        raise ValueError(f"n ({n}) が選択肢の数 ({len(choices)}) を超えています")

    # ランダムにn個選択（重複なし）
    selected = random.sample(choices, n)

    return selected


def main():
    try:
        args = sys.argv[1:]

        if not args:
            print("使用方法: python3 scripts/random_picker.py \"選択肢1\" \"選択肢2\" ... [--n 個数]", file=sys.stderr)
            sys.exit(1)

        # --n オプションの処理
        n = 1
        if "--n" in args:
            n_index = args.index("--n")
            if n_index + 1 >= len(args):
                raise ValueError("--n の後に個数を指定してください")
            n = int(args[n_index + 1])
            # --n と個数を除外
            choices = args[:n_index] + args[n_index + 2:]
        else:
            choices = args

        if not choices:
            raise ValueError("選択肢が指定されていません")

        # ランダム選択
        selected = pick_random(choices, n)

        # 結果を出力（1行に1つずつ）
        for item in selected:
            print(item)

    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"予期しないエラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
