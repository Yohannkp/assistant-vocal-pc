# Script simple pour tester Mistral API
$OLLAMA_URL = "http://127.0.0.1:11434"
$MODEL_NAME = "mistral:instruct"

Write-Host "🚀 Test de l'API Mistral via Ollama" -ForegroundColor Magenta
Write-Host "=" * 60

# Test 1: Simple question
Write-Host "`n🤖 Test 1: Question simple" -ForegroundColor Green
$body1 = '{"model": "mistral:instruct", "prompt": "Explique-moi en 2 phrases ce qu est l intelligence artificielle.", "stream": false}'
$response1 = Invoke-RestMethod -Uri "$OLLAMA_URL/api/generate" -Method POST -ContentType "application/json" -Body $body1
Write-Host "📄 Réponse:" -ForegroundColor Cyan
Write-Host $response1.response
Write-Host "⏱️  Tokens générés: $($response1.eval_count)" -ForegroundColor Yellow

# Test 2: Code Python
Write-Host "`n🤖 Test 2: Génération de code" -ForegroundColor Green
$body2 = '{"model": "mistral:instruct", "prompt": "Ecris une fonction Python pour calculer la factorielle d un nombre.", "stream": false}'
$response2 = Invoke-RestMethod -Uri "$OLLAMA_URL/api/generate" -Method POST -ContentType "application/json" -Body $body2
Write-Host "📄 Réponse:" -ForegroundColor Cyan
Write-Host $response2.response
Write-Host "⏱️  Tokens générés: $($response2.eval_count)" -ForegroundColor Yellow

# Test 3: Comparaison
Write-Host "`n🤖 Test 3: Analyse comparative" -ForegroundColor Green
$body3 = '{"model": "mistral:instruct", "prompt": "Quels sont les avantages des modeles LLM locaux par rapport aux services en ligne ?", "stream": false}'
$response3 = Invoke-RestMethod -Uri "$OLLAMA_URL/api/generate" -Method POST -ContentType "application/json" -Body $body3
Write-Host "📄 Réponse:" -ForegroundColor Cyan
Write-Host $response3.response
Write-Host "⏱️  Tokens générés: $($response3.eval_count)" -ForegroundColor Yellow

Write-Host "`n✅ Tests terminés avec succès !" -ForegroundColor Green
