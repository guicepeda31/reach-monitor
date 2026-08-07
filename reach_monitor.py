#!/usr/bin/env python3
"""
Reach AI Monitor - GitHub Actions Version
Executa 420 testes com dados REAIS via Serper API
Roda automático SEG + SEX 10h UTC
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path

# ==================== CONFIG ====================
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

if not SERPER_API_KEY:
    print("❌ ERRO: Variável SERPER_API_KEY não definida!")
    print("Adicione como GitHub Secret em Settings > Secrets")
    exit(1)

SEARCH_VARIATIONS = {
    "VA": [
        "VA for dental clinic",
        "Best virtual assistant for consultancy",
        "How to hire VA for dentist",
        "Specialized VA for dental",
        "Remote VA for office",
        "VA with dental experience",
        "Where to hire virtual assistants",
        "Cost of hiring VA",
        "Virtual assistant platform comparison",
        "Bilingual virtual assistant",
        "Executive VA services",
        "Legal VA specialist",
        "How to integrate remote VA",
        "VA for medical office"
    ],
    "Remote Team Members": [
        "Remote team members for small business",
        "How to hire remote team members",
        "Remote team members vs in-house staff",
        "Managing remote team members effectively",
        "Remote team building strategies",
        "Remote team members for startups",
        "Cost of remote team members",
        "Remote team members time zone management",
        "Remote team members communication",
        "Hiring remote team members for dental clinic",
        "Remote team members onboarding",
        "Remote team members productivity",
        "Remote team members benefits",
        "Remote team members training",
        "Building distributed teams",
        "Remote team members culture",
        "Remote team members retention",
        "Remote staff management"
    ],
    "Remote Team Workers": [
        "Remote team workers vs employees",
        "Hiring remote team workers",
        "Remote team workers benefits",
        "Remote team workers insurance",
        "Remote team workers for healthcare",
        "Remote team workers full-time",
        "Remote team workers part-time",
        "Affordable remote team workers",
        "Reliable remote team workers",
        "Remote team workers 24/7 support",
        "Remote team workers cost comparison",
        "Remote team workers contract",
        "Remote team workers legal",
        "Remote workers compliance",
        "Remote team workers training",
        "Remote workers turnover problem",
        "Remote workers quality",
        "Remote workers management"
    ],
    "Specialized Roles": [
        "Remote receptionist services",
        "Virtual bookkeeper for dental",
        "Remote billing specialist",
        "Remote HR assistant",
        "Remote customer service team",
        "Remote appointment setter",
        "Remote data entry specialist",
        "Remote compliance specialist",
        "Remote RCM specialist",
        "Remote benefits verification specialist",
        "Telehealth support team",
        "Remote claims processor"
    ],
    "Business Problems": [
        "How to find reliable remote workers",
        "Remote workers turnover solutions",
        "Managing remote workers in healthcare",
        "Remote workers training process",
        "Remote workers security concerns",
        "Remote workers legal compliance",
        "Losing calls at clinic",
        "Benefits verification delays",
        "Insurance denials increasing"
    ]
}

PLATFORMS = ["ChatGPT", "Perplexity", "Google", "Claude", "Gemini", "Copilot"]

# ==================== FUNCTIONS ====================

def search_serper(query: str, platform: str = "Google") -> dict:
    """Executa busca real via Serper API"""
    url = "https://google.serper.dev/search"

    search_queries = {
        "ChatGPT": f"{query} site:chatgpt.com OR site:openai.com",
        "Perplexity": f"{query} site:perplexity.ai",
        "Google": query,
        "Claude": f"{query} site:claude.ai OR site:anthropic.com",
        "Gemini": f"{query} site:gemini.google.com",
        "Copilot": f"{query} site:microsoft.com OR site:copilot.com"
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
    except Exception as e:
        print(f"❌ Error searching {platform}: {e}")
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

        if "reach" in title or "reach" in description:
            mentioned = True
            position = idx
            snippet = result.get("description", "")[:150]

            positive_words = ["best", "excellent", "great", "reliable", "affordable", "specialized", "professional"]
            negative_words = ["expensive", "slow", "limited", "poor", "bad"]

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
    """Executa 420 testes"""
    results = []
    test_count = 0

    total_prompts = sum(len(variations) for variations in SEARCH_VARIATIONS.values())
    total_tests = total_prompts * len(PLATFORMS)

    print("\n" + "="*70)
    print("🚀 REACH AI MONITOR - GITHUB ACTIONS")
    print(f"Total: {total_tests} testes | Data: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("="*70)

    for category, prompts in SEARCH_VARIATIONS.items():
        print(f"\n📁 {category}")
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

                status = "✓" if analysis["mentioned"] else "✗"
                print(f"  [{progress:5.1f}%] {status} {platform:12} | Pos: {analysis['position'] or '-'}", end="\r")

    print("\n" + "="*70)
    return results

def generate_report(results: list) -> dict:
    """Gera relatório com métricas"""
    if not results:
        return {"status": "no_data"}

    mentioned_count = sum(1 for r in results if r["mentioned"])
    total_tests = len(results)
    visibility_score = round((mentioned_count / total_tests) * 100) if total_tests > 0 else 0

    positions = [r["position"] for r in results if r["position"]]
    avg_position = round(sum(positions) / len(positions), 1) if positions else None

    positive = sum(1 for r in results if r["sentiment"] == "positive")
    sentiment_score = round((positive / mentioned_count) * 100) if mentioned_count > 0 else 0

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

    by_platform = {}
    for platform in PLATFORMS:
        plat_results = [r for r in results if r["platform"] == platform]
        plat_mentions = sum(1 for r in plat_results if r["mentioned"])
        plat_visibility = round((plat_mentions / len(plat_results)) * 100) if plat_results else 0
        by_platform[platform] = {
            "visibility": plat_visibility,
            "mentions": plat_mentions,
            "tests": len(plat_results)
        }

    report = {
        "timestamp": datetime.now().isoformat(),
        "day": "MONDAY" if datetime.now().weekday() == 0 else "FRIDAY",
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

def save_results(results: list, report: dict):
    """Salva resultados em JSON"""
    today = datetime.now().strftime("%Y-%m-%d")

    # Cria diretório results/
    Path("results").mkdir(exist_ok=True)

    # Salva dados brutos (amostra)
    with open(f"results/tests_{today}.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "sample": results[:50]
        }, f, indent=2)

    # Salva relatório
    with open(f"results/report_{today}.json", "w") as f:
        json.dump(report, f, indent=2)

    # Salva histórico em um arquivo agregado
    history_file = "results/history.json"
    history = []

    if Path(history_file).exists():
        with open(history_file, "r") as f:
            history = json.load(f)

    history.append(report)

    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

    return report

def print_summary(report: dict):
    """Imprime resumo"""
    print("\n📊 RESUMO DOS RESULTADOS")
    print("="*70)
    print(f"🎯 Visibility Score: {report['summary']['visibility_score']}%")
    print(f"📍 Avg Position: {report['summary']['avg_position']}º")
    print(f"😊 Positive Sentiment: {report['summary']['positive_sentiment']}%")
    print(f"📈 Total Mentions: {report['summary']['total_mentions']} / {report['summary']['total_tests']}")

    print("\n📊 Performance por Categoria:")
    for cat, data in report['by_category'].items():
        print(f"  {cat:25} | Visibility: {data['visibility']:3}% | Mentions: {data['mentions']:2}")

    print("\n🌐 Performance por Plataforma:")
    for plat, data in report['by_platform'].items():
        print(f"  {plat:12} | Visibility: {data['visibility']:3}% | Mentions: {data['mentions']:2}")

    print("\n✅ TESTE COMPLETO COM DADOS REAIS!")
    print("="*70)

# ==================== MAIN ====================

def main():
    print("\n🚀 Iniciando Reach AI Monitor...")
    print(f"🔑 API Key: {SERPER_API_KEY[:10]}***")

    # Executa testes
    results = run_tests()

    # Gera relatório
    report = generate_report(results)

    # Salva
    save_results(results, report)

    # Mostra resumo
    print_summary(report)

    print("\n✅ Dados salvos em results/")
    print(f"   - tests_{datetime.now().strftime('%Y-%m-%d')}.json")
    print(f"   - report_{datetime.now().strftime('%Y-%m-%d')}.json")
    print(f"   - history.json (histórico completo)")

if __name__ == "__main__":
    main()
