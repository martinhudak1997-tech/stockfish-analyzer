#!/usr/bin/env python3
"""Analyze one chess FEN with the official Stockfish binary (UCI)."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import chess
import chess.engine


def read_position():
    fen = os.environ.get("FEN_OVERRIDE", "").strip()
    if not fen:
        fen = Path("requests/position.fen").read_text(encoding="utf-8").strip()
    if fen.lower() in {"startpos", "start"}:
        return chess.Board()
    board = chess.Board(fen)
    if not board.is_valid():
        raise ValueError("The FEN is not a valid, legal chess position: " + fen)
    return board


def score_as_json(score):
    if score is None:
        return None
    return {
        "centipawns": score.score(),
        "mate_in": score.mate(),
    }


def main():
    board = read_position()
    seconds = max(1, min(30, int(os.environ.get("ANALYSIS_SECONDS", "10"))))
    binary = os.environ.get("STOCKFISH_BIN")
    if not binary:
        raise RuntimeError("STOCKFISH_BIN is not set.")

    output = {
        "analyzed_at_utc": datetime.now(timezone.utc).isoformat(),
        "engine": "Stockfish 19 (official release)",
        "fen": board.fen(),
        "side_to_move": "white" if board.turn == chess.WHITE else "black",
        "seconds_per_position": seconds,
        "is_game_over": board.is_game_over(claim_draw=True),
        "variations": [],
    }

    if board.is_game_over(claim_draw=True):
        outcome = board.outcome(claim_draw=True)
        output["outcome"] = str(outcome) if outcome else "Game over"
    else:
        with chess.engine.SimpleEngine.popen_uci(binary, timeout=45.0) as engine:
            engine.configure({"Threads": 2, "Hash": 128})
            analyses = engine.analyse(
                board, chess.engine.Limit(time=seconds), multipv=3
            )
            for rank, info in enumerate(analyses, 1):
                pv = info.get("pv", [])
                if not pv:
                    continue
                pov_score = info["score"]
                output["variations"].append({
                    "rank": rank,
                    "best_move_san": board.san(pv[0]),
                    "best_move_uci": pv[0].uci(),
                    "principal_variation_san": board.variation_san(pv[:10]),
                    "principal_variation_uci": [m.uci() for m in pv[:10]],
                    "evaluation_for_side_to_move": score_as_json(pov_score.pov(board.turn)),
                    "evaluation_for_white": score_as_json(pov_score.white()),
                    "depth": info.get("depth"),
                    "seldepth": info.get("seldepth"),
                    "nodes": info.get("nodes"),
                })

    destination = Path("results/latest.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
