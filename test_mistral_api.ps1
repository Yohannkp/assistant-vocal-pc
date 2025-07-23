# Test de l'API Mistral avec PowerShell

# Configuration
$OLLAMA_URL = "http://127.0.0.1:11434"
$MODEL_NAME = "mistral:instruct"

function Test-MistralAPI {
    param(
        [string]$Prompt,
        [bool]$Stream = $false
    )
    
    $url = "$OLLAMA_URL/api/generate"
    
    $body = @{
        model = $MODEL_NAME
        prompt = $Prompt
        stream = $Stream
    } | ConvertTo-Json
    
    Write-Host "🤖 Envoi de la requête à Mistral..." -ForegroundColor Green
    Write-Host "📝 Prompt: $Prompt" -ForegroundColor Cyan
    Write-Host ("-" * 50)
    
    $startTime = Get-Date
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method POST -ContentType "application/json" -Body $body
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        Write-Host "✅ Réponse de Mistral:" -ForegroundColor Green
        Write-Host "📄 $($response.response)" -ForegroundColor White
        Write-Host ("-" * 50)
        Write-Host "⏱️  Temps de réponse: $([math]::Round($duration, 2)) secondes" -ForegroundColor Yellow
        Write-Host "🔢 Tokens générés: $($response.eval_count)" -ForegroundColor Yellow
        
        return $response
    }
    catch {
        Write-Host "❌ Erreur lors de la requête: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

function Get-AvailableModels {
    $url = "$OLLAMA_URL/api/tags"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method GET
        
        Write-Host "📋 Modèles disponibles:" -ForegroundColor Green
        foreach ($model in $response.models) {
            $sizeGB = [math]::Round($model.size / 1GB, 1)
            Write-Host "  - $($model.name) (Taille: $sizeGB GB)" -ForegroundColor Cyan
        }
        
        return $response.models
    }
    catch {
        Write-Host "❌ Erreur lors de la récupération des modèles: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Tests
Write-Host "🚀 Test de l'API Mistral via Ollama" -ForegroundColor Magenta
Write-Host ("=" * 60)

# Afficher les modèles disponibles
Get-AvailableModels
Write-Host ""

# Test simple
Test-MistralAPI -Prompt "Explique-moi en 2 phrases ce qu'est l'intelligence artificielle."
Write-Host ""

# Test avec du code
Test-MistralAPI -Prompt "Écris une fonction Python pour calculer la factorielle d'un nombre."
Write-Host ""

# Test de conversation
Test-MistralAPI -Prompt "Quels sont les avantages des modeles LLM locaux par rapport aux services en ligne ?"
