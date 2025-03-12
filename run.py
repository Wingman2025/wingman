import os
from app import app

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto que Railway asigna
    app.run(debug=False, host='0.0.0.0', port=port)

