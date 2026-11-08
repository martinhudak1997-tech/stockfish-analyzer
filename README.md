# Stockfish analyzer

Automatická analýza šachových pozic pomocí **Stockfish 19** a GitHub Actions. Výsledek je čitelný přes připojení GitHub v ChatGPT.

## Použití z ChatGPT

1. Napiš „Analyzuj tuto pozici přes Stockfish“ a přidej **FEN** nebo čitelný obrázek šachovnice s informací, kdo je na tahu. U fotografie musí být všechny figurky a orientace polí jednoznačné.
2. ChatGPT může zapsat FEN do `requests/position.fen`, což spustí workflow.
3. Jakmile workflow dokončí analýzu, ChatGPT může přes GitHub načíst `results/latest.json` a vysvětlit nejsilnější tah i alternativy. GitHub Actions mají frontu a nejsou vhodné pro okamžité rozhodování v rychlé partii.

## Ruční spuštění z GitHubu

Otevři [Actions → Stockfish 19 — analysis](../../actions/workflows/analyze.yml), zvol **Run workflow**, vlož FEN a klikni na **Run workflow**. Bez FEN workflow použije obsah `requests/position.fen`. Výchozí čas analýzy je 10 sekund, přípustné rozpětí 1–30 s.

## Vstup a výstup

- Vstup: `requests/position.fen` (jedna FEN pozice nebo `startpos`).
- Výstup: `results/latest.json` — tři nejlepší varianty (MultiPV), tahy v SAN/UCI, hodnocení z pohledu bílého a hráče na tahu, přibližná hloubka prohledávání.
- Workflow spouští oficiální Stockfish 19 na GitHub runneru, výsledky commitne na větev `main`.
- Pro soukromé analýzy nastav repozitář jako **Private**. V současnosti je viditelný všem, pokud jej nezměníš.

Provoz GitHub Actions se řídí limity GitHubu. Verze Stockfish a workflow jsou nastaveny explicitně, ale GitHub Actions mohou v budoucnu vyžadovat aktualizace.
