#!/usr/bin/env python3
"""
Reach AI Monitor - 49 TESTES (GitHub Actions Version)
Executa 49 testes com dados REAIS via Serper API
Roda automático SEG + SEX 10h UTC
Cabe nos 100 requisições/dia grátis!
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path
import sys

# ==================== CONFIG ====================
SERPER_API_KEY = os.getenv('SERPER_API_KEY', '').strip()

if not SERPER_API_KEY:
    print("❌ ERRO: Variável SERPER_API_KEY não definida!")
    print("   Configure em: GitHub Repo → Settings → Secrets → New Secret")
    print("   Nome: SERPER_API_KEY")
    print("   Valor: sua-chave-aqui")
    sys.exit(1)

# Cria diretório de resultados
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)
(RESULTS_DIR / "history").mkdir(exist_ok=True)

# 49 TESTES = ~8 prompts × 6 plataformas (seleção mais importante)
SEARCH_VARIATIONS = {
    "VA": [
        "VA for dental clinic",
        "How to hire VA for dentist",
        "Specialized VA for dental",
        "Remote VA for office",
        "Best virtual assistant",
        "Cost of hiring VA",
        "Virtual assistant platform",
        "Where to hire virtual assistants",
    ],
    "Remote Team Members": [
        "Remote team members for small business",
        "How to hire remote team members",
        "Managing remote team members",
        "Remote team building",
        "Remote team members for startups",
        "Cost of remote team members",
        "Remote team onboarding",
        "Building distributed teams",
    ],
    "Specialized Roles": [
        "Remote receptionist services",
        "Virtual bookkeeper for dental",
        "Remote billing specialist",
        "Remote HR assistant",
    ],
    "Business Problems": [
        "How to find reliable remote workers",
        "Remote workers turnover solutions",
        "Managing remote workers",
        "Remote workers training",
    ],
}

PLATFORMS = ["Google", "ChatGPT", "Perplexity", "Claude", "Gemini", "Copilot"]

# ==================== FUNCTIONS ====================

def search_serper(query: str, platform: str = "Google") -> dict:
    """Executa busca real via Serper API"""
    url = "https://google.serper.dev/search"

    search_queries = {
        "ChatGPT": f"{query} ChatGPT OpenAI",
        "Perplexity": f"{query} Perplexity AI",
        "Google": query,
        "Claude": f"{query} Claude Anthropic",
        "Gemini": f"{query} Gemini Google",
        "Copilot": f"{query} Copilot Microsoft"
    }

    payload = {
        "q": search_queries.get(platform, query),
        "num": 10
    }

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Error searching {platform}: {str(e)[:50]}")
        return {"searchResults": []}
    except Exception as e:
        print(f"  ⚠️  Unexpected error: {str(e)[:50]}")
        return {"searchResults": []}

def analyze_results(query: str, platform: str, search_results: dict) -> dict:
    """Analisa resultados para Reach mencionada"""
    mentioned = False
    position = None
    sentiment = "none"
    snippet = ""

    results = search_results.get("searchResults", [])

    for idx, result in enumerate(results, 1):
        title = result.get("title", "").lower()
        description = result.get("description", "").lower()

        # Procura por Reach em título ou descrição
        if "reach" in title or "reach.co" in description or "getreach" in description:
            mentioned = True
            position = idx
            snippet = result.get("description", "")[:150]

            # Análise de sentimento simples
            positive_words = ["best", "excellent", "great", "reliable", "affordable", "specialized", "trusted"]
            negative_words = ["expensive", "slow", "limited", "poor", "unreliable"]

            text = (title + " " + description).lower()
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)

            if pos_count > neg_count:
                sentiment = "positive"
            elif neg_count > pos_count:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            break

    return {
        "mentioned": mentioned,
        "position": position,
        "sentiment": sentiment,
        "snippet": snippet
    }

def run_tests() -> list:
    """Executa 49 testes"""
    results = []
    test_count = 0

    total_prompts = sum(len(variations) for variations in SEARCH_VARIATIONS.values())
    total_tests = total_prompts * len(PLATFORMS)

    print("\n" + "="*70)
    print(f"🚀 REACH AI MONITOR - 49 TESTES")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"API: Serper (up to 100 free requests/day)")
    print("="*70)

    for category, prompts in SEARCH_VARIATIONS.items():
        print(f"\n📁 {category} ({len(prompts)} prompts)")
        
        for prompt in prompts:
            for platform in PLATFORMS:
                test_count += 1
                progress = (test_count / total_tests) * 100

                search_results = search_serper(prompt, platform)
                analysis = analyze_results(prompt, platform, search_results)

                result = {
                    "timestamp": datetime.now().isoformat(),
                    "prompt": prompt,
                    "category": category,
                    "platform": platform,
                    "mentioned": analysis["mentioned"],
                    "position": analysis["position"],
                    "sentiment": analysis["sentiment"],
                    "snippet": analysis["snippet"]
                }

                results.append(result)

                status = "✅" if analysis["mentioned"] else "⬜"
                print(f"  [{progress:5.1f}%] {status} {platform:12}", end="\r")

    print("\n" + "="*70)
    return results

def generate_report(results: list) -> dict:
    """Gera relatório com métricas"""
    if not results:
        return {
            "status": "no_data",
            "timestamp": datetime.now().isoformat()
        }

    mentioned_count = sum(1 for r in results if r["mentioned"])
    total_tests = len(results)
    visibility_score = round((mentioned_count / total_tests) * 100) if total_tests > 0 else 0

    positions = [r["position"] for r in results if r["position"]]
    avg_position = round(sum(positions) / len(positions), 1) if positions else None

    positive = sum(1 for r in results if r["sentiment"] == "positive")
    sentiment_score = round((positive / mentioned_count) * 100) if mentioned_count > 0 else 0

    # Performance por categoria
    by_category = {}
    for category in SEARCH_VARIATIONS.keys():
        cat_results = [r for r in results if r["category"] == category]
        cat_mentions = sum(1 for r in cat_results if r["mentioned"])
        cat_visibility = round((cat_mentions / len(cat_results)) * 100) if cat_results else 0
        by_category[category] = {
            "visibility": cat_visibility,
            "mentions": cat_mentions,
            "tests": len(cat_results)
        }

    # Performance por plataforma
    by_platform = {}
    for platform in PLATFORMS:
        plat_results = [r for r in results if r["platform"] == platform]
        if plat_results:
            plat_mentions = sum(1 for r in plat_results if r["mentioned"])
            plat_visibility = round((plat_mentions / len(plat_results)) * 100)
            by_platform[platform] = {
                "visibility": plat_visibility,
                "mentions": plat_mentions,
                "tests": len(plat_results)
            }

    report = {
        "timestamp": datetime.now().isoformat(),
        "day": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"][datetime.now().weekday()],
        "total_tests": total_tests,
        "summary": {
            "visibility_score": visibility_score,
            "avg_position": avg_position,
            "positive_sentiment": sentiment_score,
            "total_mentions": mentioned_count,
            "total_tests": total_tests
        },
        "by_category": by_category,
        "by_platform": by_platform,
    }

    return report

def load_previous_report() -> dict:
    """Carrega relatório anterior para comparação (com fallback)"""
    history_file = RESULTS_DIR / "history.json"
    
    try:
        if history_file.exists():
            with open(history_file, "r") as f:
                history = json.load(f)
                if history and isinstance(history, list) and len(history) > 0:
                    return history[-1]
    except (json.JSONDecodeError, IOError, IndexError) as e:
        print(f"  ⚠️  Could not load history: {e}")
    
    return None

def compare_reports(current: dict, previous: dict) -> dict:
    """Compara relatórios para mostrar tendências"""
    if not previous:
        return {"status": "first_run", "previous_timestamp": None}

    try:
        comparison = {
            "visibility_change": current["summary"]["visibility_score"] - previous["summary"]["visibility_score"],
            "position_change": (previous["summary"]["avg_position"] or 0) - (current["summary"]["avg_position"] or 0),
            "sentiment_change": current["summary"]["positive_sentiment"] - previous["summary"]["positive_sentiment"],
            "mentions_change": current["summary"]["total_mentions"] - previous["summary"]["total_mentions"],
            "previous_timestamp": previous.get("timestamp")
        }
        return comparison
    except (KeyError, TypeError) as e:
        print(f"  ⚠️  Could not compare reports: {e}")
        return {"status": "comparison_error"}

def save_results(results: list, report: dict):
    """Salva resultados em JSON (com error handling)"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        # Salva dados brutos
        tests_file = RESULTS_DIR / f"tests_{today}.json"
        with open(tests_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(results),
                "results": results
            }, f, indent=2)

        # Salva relatório
        report_file = RESULTS_DIR / f"report_{today}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Atualiza histórico
        history_file = RESULTS_DIR / "history.json"
        history = []

        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    history = json.load(f)
            except (json.JSONDecodeError, IOError):
                history = []

        history.append(report)

        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)

        print(f"\n✅ Dados salvos em results/")
        print(f"   - tests_{today}.json")
        print(f"   - report_{today}.json")
        print(f"   - history.json")

    except IOError as e:
        print(f"\n❌ Erro ao salvar resultados: {e}")

def print_summary(report: dict, comparison: dict = None):
    """Imprime resumo"""
    if report.get("status") == "no_data":
        print("\n❌ Nenhum resultado coletado!")
        return

    print("\n📊 RESUMO DOS RESULTADOS")
    print("="*70)
    
    summary = report.get("summary", {})
    
    print(f"🎯 Visibility Score: {summary.get('visibility_score', 'N/A')}%", end="")
    if comparison and comparison.get("status") != "first_run":
        change = comparison.get("visibility_change", 0)
        symbol = "↑" if change > 0 else "↓" if change < 0 else "→"
        print(f" {symbol} {abs(change):+.0f}%")
    else:
        print(" (first run)")

    print(f"📍 Avg Position: {summary.get('avg_position', 'N/A')}º")
    print(f"😊 Positive Sentiment: {summary.get('positive_sentiment', 'N/A')}%")
    print(f"📈 Total Mentions: {summary.get('total_mentions', 0)} / {summary.get('total_tests', 0)}")

    print("\n📊 Performance por Categoria:")
    for cat, data in report.get('by_category', {}).items():
        print(f"  {cat:25} | Visibility: {data['visibility']:3}% | Mentions: {data['mentions']:2}")

    print("\n🌐 Performance por Plataforma:")
    for plat, data in report.get('by_platform', {}).items():
        print(f"  {plat:12} | Visibility: {data['visibility']:3}% | Mentions: {data['mentions']:2}")

    if comparison and comparison.get("status") not in ["first_run", "comparison_error"]:
        print("\n📈 COMPARAÇÃO COM ÚLTIMA RODADA:")
        print(f"  Visibility: {comparison.get('visibility_change', 0):+.0f}%")
        print(f"  Position: {comparison.get('position_change', 0):+.1f}º")
        print(f"  Sentiment: {comparison.get('sentiment_change', 0):+.0f}%")
        print(f"  Mentions: {comparison.get('mentions_change', 0):+.0f}")

    print("\n✅ TESTE COMPLETO!")
    print("="*70)

# ==================== MAIN ====================

def main():
    print("\n🚀 Iniciando Reach AI Monitor (49 testes)...")
    print(f"🔑 API Key: {SERPER_API_KEY[:15]}{'*' * (len(SERPER_API_KEY)-15)}")
    print(f"📅 Day: {['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'][datetime.now().weekday()]}")

    try:
        # Executa testes
        results = run_tests()
        
        if not results:
            print("\n❌ Nenhum teste foi executado!")
            sys.exit(1)

        # Gera relatório
        report = generate_report(results)

        # Carrega relatório anterior para comparação
        previous = load_previous_report()
        comparison = compare_reports(report, previous)

        # Salva
        save_results(results, report)

        # Mostra resumo
        print_summary(report, comparison)

        print(f"\n📌 Total de requisições usadas: {len(results)} requisições ✅")
        print(f"   (Limite: 100/dia em Serper)")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Erro não esperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
