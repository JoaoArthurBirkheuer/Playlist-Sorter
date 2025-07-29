# 🎵 Organizador de Playlists do Spotify

Este projeto é um script em Python que organiza suas playlists do Spotify com base em diferentes critérios de ordenação. Ele se conecta à sua conta do Spotify via API e permite reordenar faixas de maneira simples e interativa pelo terminal.

---

## Pré-requisitos

Antes de começar, certifique-se de ter o seguinte instalado na sua máquina:

- **[Python 3.7+](https://www.python.org/downloads/)**  
- **pip**

Clone este repositório na sua máquina:

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```

---

## Configuração do Ambiente Virtual

É recomendável usar um ambiente virtual para isolar as dependências do projeto:

### 1. Criar o ambiente:

```bash
python -m venv .venv
```

### 2. Ativar o ambiente:

- **Windows:**

  ```bash
  .venv\Scripts\activate
  ```

- **macOS / Linux:**

  ```bash
  source .venv/bin/activate
  ```

### 3. Instalar as dependências:

```bash
pip install -r requirements.txt
```

---

## Configurar Aplicativo no Spotify

Para usar a API do Spotify, você precisa registrar seu próprio aplicativo no [Dashboard de Desenvolvedores do Spotify](https://developer.spotify.com/dashboard/):

### Passos:

1. Acesse o [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Faça login com sua conta do Spotify.
3. Clique em **"Create App"** e preencha os campos necessários.
4. Após criar, clique em **"Edit Settings"**.
5. Em **Redirect URIs**, adicione exatamente:

   ```
   http://127.0.0.1:8888/callback
   ```

6. Clique em **Add** e depois em **Save**.
7. Copie o **Client ID** e o **Client Secret**.

---

## Variáveis de Ambiente

Na raiz do projeto, crie um arquivo chamado `.env` com o seguinte conteúdo:

```env
SPOTIPY_CLIENT_ID=SEU_CLIENT_ID_AQUI
SPOTIPY_CLIENT_SECRET=SEU_CLIENT_SECRET_AQUI
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
SPOTIPY_CACHE_PATH=.spotify_token_cache.json
```

---

## Executar o Script

Com o ambiente virtual ativado, execute o script:

```bash
python playlistSorter.py
```

---

## Como Usar

1. **Autenticação:**  
   Na primeira execução (ou se o token expirar), será aberta uma aba no navegador para autenticação. Faça login e autorize o app.

2. **Seleção de Playlist:**  
   O terminal listará suas playlists. Digite o número correspondente à playlist que deseja ordenar ou `0` para sair.

3. **Escolha do Critério de Ordenação:**

   ```
   1 - Nome da faixa (A-Z)
   2 - Nome da faixa (Z-A)
   3 - Nome do artista (A-Z)
   4 - Nome do artista (Z-A)
   5 - Data de adição (Mais recentes primeiro)
   6 - Data de adição (Mais antigas primeiro)
   ```

   Escolha o número desejado ou `0` para cancelar.

4. **Confirmação:**  
   Você será solicitado a confirmar a ordenação antes que ela ocorra (`s` para sim, `n` para não).

---

## ⚠️ Aviso Importante

> O processo de ordenação **remove todas as faixas da playlist** e as **adiciona novamente na nova ordem**.  
> Isso significa que a ordem original será **permanentemente perdida**.
