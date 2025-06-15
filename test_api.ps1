# Script PowerShell para probar la Companion App API
# Asegúrate de que el servidor esté corriendo en http://127.0.0.1:5000

Write-Host "🧪 Probando Companion App API..." -ForegroundColor Green

# 1. Obtener plantillas de objetivos
Write-Host "`n1. 📋 Plantillas de Objetivos:" -ForegroundColor Yellow
curl -X GET "http://127.0.0.1:5000/api/goal_templates" -H "Content-Type: application/json"

# 2. Obtener badges disponibles
Write-Host "`n`n2. 🏆 Badges Disponibles:" -ForegroundColor Yellow
curl -X GET "http://127.0.0.1:5000/api/badges" -H "Content-Type: application/json"

# 3. Crear un objetivo (necesita user_id en sesión)
Write-Host "`n`n3. 🎯 Crear Objetivo (requiere login):" -ForegroundColor Yellow
$createGoalData = @{
    goal_template_id = 1
    custom_title = "Mi primer objetivo de jibe"
    target_value = 15
} | ConvertTo-Json

curl -X POST "http://127.0.0.1:5000/api/create_goal" `
     -H "Content-Type: application/json" `
     -d $createGoalData

# 4. Obtener objetivos del usuario (requiere login)
Write-Host "`n`n4. 📊 Objetivos del Usuario (requiere login):" -ForegroundColor Yellow
curl -X GET "http://127.0.0.1:5000/api/user_goals" -H "Content-Type: application/json"

# 5. Estadísticas de sesiones (requiere login)
Write-Host "`n`n5. 📈 Estadísticas de Sesiones (requiere login):" -ForegroundColor Yellow
curl -X GET "http://127.0.0.1:5000/api/session_stats" -H "Content-Type: application/json"

Write-Host "`n`n✅ Pruebas completadas!" -ForegroundColor Green
Write-Host "💡 Nota: Los endpoints que requieren login necesitan que te autentiques primero en la web app" -ForegroundColor Cyan
