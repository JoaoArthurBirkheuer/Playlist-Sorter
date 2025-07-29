import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect
import os
import datetime
import sys
import time

from dotenv import load_dotenv
load_dotenv()

# --- CONFIGURAÇÕES DO APLICATIVO SPOTIFY ---

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
CACHE_PATH = os.getenv('SPOTIPY_CACHE_PATH', '.spotify_token_cache.json')

if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    print("Erro: CLIENT_ID, CLIENT_SECRET ou REDIRECT_URI não configurados no arquivo .env.")
    print("Certifique-se de que seu arquivo .env está correto e na mesma pasta do script.")
    sys.exit(1)

SCOPE = (
    'user-read-private '
    'playlist-read-private '
    'playlist-read-collaborative '
    'playlist-modify-public '
    'playlist-modify-private'
)

app = Flask(__name__)
sp_oauth = None
sp = None

@app.route('/')
def index():
    global sp_oauth
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=CACHE_PATH
    )

    token_info = sp_oauth.get_cached_token()
    if token_info and sp_oauth.validate_token(token_info):
        print("Token encontrado e válido no cache. Autenticado.")
        return redirect('/authenticated')
    else:
        auth_url = sp_oauth.get_authorize_url()
        print(f"Abra esta URL no seu navegador para autenticar: {auth_url}")
        return f"Redirecionando para autenticação do Spotify... <a href='{auth_url}'>Clique aqui se não for redirecionado.</a>"

@app.route('/callback')
def callback():
    global sp, sp_oauth
    code = request.args.get('code')

    if not sp_oauth:
        sp_oauth = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            cache_path=CACHE_PATH
        )

    if code:
        try:
            token_info = sp_oauth.get_access_token(code, as_dict=True)
            sp = spotipy.Spotify(auth=token_info['access_token'])
            print("\nAutenticação bem-sucedida! Retornando ao terminal...")
            func = request.environ.get('werkzeug.server.shutdown')
            if func is not None:
                func()
            return "<h1>Autenticação concluída! Você pode fechar esta aba e retornar ao terminal.</h1>"
        except Exception as e:
            print(f"Erro ao obter token: {e}")
            return "<h1>Erro na autenticação.</h1><p>Por favor, tente novamente no terminal.</p>"
    else:
        return "<h1>Erro na autenticação.</h1><p>Nenhum código de autorização recebido.</p>"

@app.route('/authenticated')
def authenticated_from_cache():
    global sp, sp_oauth
    if not sp_oauth:
         sp_oauth = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            cache_path=CACHE_PATH
        )
    token_info = sp_oauth.get_cached_token()
    if token_info and sp_oauth.validate_token(token_info):
        sp = spotipy.Spotify(auth=token_info['access_token'])
        func = request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
        return "<h1>Autenticação concluída via cache! Você pode fechar esta aba e retornar ao terminal.</h1>"
    else:
        return redirect('/')

def get_user_playlists(spotify_obj):
    """Obtém todas as playlists do usuário."""
    playlists = []
    results = spotify_obj.current_user_playlists()
    while results:
        for i, playlist in enumerate(results['items']):
            playlists.append(playlist)
        if results['next']:
            results = spotify_obj.next(results)
        else:
            results = None
    return playlists

def get_playlist_tracks(spotify_obj, playlist_id):
    """Obtém todas as faixas de uma playlist."""
    tracks = []
    results = spotify_obj.playlist_items(playlist_id)
    while results:
        for item in results['items']:
            if item['track'] and item['track']['id']:
                tracks.append(item)
        if results['next']:
            results = spotify_obj.next(results)
        else:
            results = None
    return tracks

def sort_tracks(tracks, criterion, order):
    """Ordena as faixas com base no critério e ordem."""
    if not tracks:
        return []

    if criterion == 1: # Nome da música (Ascendente)
        return sorted(tracks, key=lambda x: x['track']['name'].lower())
    elif criterion == 2: # Nome da música (Descendente)
        return sorted(tracks, key=lambda x: x['track']['name'].lower(), reverse=True)
    elif criterion == 3: # Nome do artista (Ascendente)
        return sorted(tracks, key=lambda x: x['track']['artists'][0]['name'].lower() if x['track']['artists'] else '')
    elif criterion == 4: # Nome do artista (Descendente)
        return sorted(tracks, key=lambda x: x['track']['artists'][0]['name'].lower() if x['track']['artists'] else '', reverse=True)
    elif criterion == 5: # Data de adição (Mais recentes primeiro)
        return sorted(tracks, key=lambda x: datetime.datetime.fromisoformat(x['added_at'].replace('Z', '+00:00')), reverse=True)
    elif criterion == 6: # Data de adição (Mais antigas primeiro)
        return sorted(tracks, key=lambda x: datetime.datetime.fromisoformat(x['added_at'].replace('Z', '+00:00')))
    else:
        return tracks

def confirm_action(prompt):
    """Pede confirmação ao usuário."""
    while True:
        response = input(f"{prompt} (s/n): ").lower().strip()
        if response == 's':
            return True
        elif response == 'n':
            return False
        else:
            print("Resposta inválida. Por favor, digite 's' para sim ou 'n' para não.")

def main_cli_loop():
    """Loop principal da interface de linha de comando."""
    global sp

    if not sp:
        print("Erro: Objeto Spotipy não inicializado. Tente rodar o script novamente.")
        return

    print("\n--- BEM-VINDO AO ORGANIZADOR DE PLAYLISTS SPOTIFY ---")
    try:
        user = sp.current_user()
        print(f"Olá, {user['display_name']}!")
    except spotipy.exceptions.SpotifyException as e:
        print(f"Erro ao obter informações do usuário: {e}")
        print("Seu token de acesso pode ter expirado. Por favor, reinicie o script para reautenticar.")
        return 

    while True:
        print("\nObtendo suas playlists...")
        playlists = get_user_playlists(sp)

        if not playlists:
            print("Nenhuma playlist encontrada na sua conta.")
            break

        print("\n--- SUAS PLAYLISTS ---")
        for i, playlist in enumerate(playlists):
            print(f"[{i+1}] {playlist['name']} ({playlist['tracks']['total']} faixas)")
        print("[0] Sair")

        try:
            choice = int(input("Escolha o número da playlist para ordenar (ou 0 para sair): "))
            if choice == 0:
                print("Saindo do programa. Até mais!")
                break
            
            if not (1 <= choice <= len(playlists)):
                print("Escolha inválida. Por favor, digite um número da lista.")
                continue

            selected_playlist = playlists[choice - 1]
            playlist_id = selected_playlist['id']
            playlist_name = selected_playlist['name']

            print(f"\nPlaylist selecionada: '{playlist_name}'")
            print("\n--- ESCOLHA O CRITÉRIO DE ORDENAÇÃO ---")
            print("  0 - Cancelar e voltar à seleção de playlist")
            print("  1 - Nome da faixa (A-Z)")
            print("  2 - Nome da faixa (Z-A)")
            print("  3 - Nome do artista (A-Z)")
            print("  4 - Nome do artista (Z-A)")
            print("  5 - Data de adição (Mais recentes primeiro)")
            print("  6 - Data de adição (Mais antigas primeiro)")

            sort_choice = int(input("Escolha o número do critério de ordenação: "))

            if sort_choice == 0:
                continue 

            if not (1 <= sort_choice <= 6):
                print("Critério de ordenação inválido. Por favor, escolha um número da lista.")
                continue
            
            if not confirm_action(f"Tem certeza que deseja ordenar a playlist '{playlist_name}'? Esta ação irá modificar a ordem das faixas."):
                print("Operação cancelada.")
                continue

            print(f"\nObtendo faixas da playlist '{playlist_name}'...")
            tracks_info = get_playlist_tracks(sp, playlist_id)

            if not tracks_info:
                print(f"A playlist '{playlist_name}' está vazia ou não contém faixas válidas. Nada para ordenar.")
                continue

            original_track_ids = [t['track']['id'] for t in tracks_info if t['track']]
            print(f"Total de faixas encontradas: {len(original_track_ids)}")

            print("Ordenando faixas...")
            sorted_tracks_info = sort_tracks(tracks_info, sort_choice, None)
            sorted_track_ids = [t['track']['id'] for t in sorted_tracks_info if t['track']]

            if not sorted_track_ids:
                print("Não foi possível extrair IDs das faixas ordenadas. Verifique a estrutura dos dados.")
                continue

            if original_track_ids == sorted_track_ids:
                print("A playlist já está na ordem desejada. Nenhuma alteração necessária.")
                continue

            print("Removendo faixas existentes e adicionando-as na nova ordem...")
            chunk_size = 100
            for i in range(0, len(original_track_ids), chunk_size):
                chunk = original_track_ids[i:i + chunk_size]
                sp.playlist_remove_all_occurrences_of_items(playlist_id, chunk)
                time.sleep(0.1)

            for i in range(0, len(sorted_track_ids), chunk_size):
                chunk = sorted_track_ids[i:i + chunk_size]
                sp.playlist_add_items(playlist_id, chunk)
                time.sleep(0.1)

            print(f"\nPlaylist '{playlist_name}' ordenada com sucesso!")

        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")
        except spotipy.exceptions.SpotifyException as e:
            print(f"Erro da API do Spotify: {e}")
            if "The access token expired" in str(e):
                print("Seu token de acesso expirou. Por favor, tente autenticar novamente (reinicie o script).")
                break
            elif "not found" in str(e).lower() and "playlist" in str(e).lower():
                print("A playlist não foi encontrada ou você não tem permissão. Verifique o ID.")
            elif "permission" in str(e).lower():
                print("Você não tem permissão para modificar esta playlist. Verifique os escopos.")
            else:
                print("Um erro inesperado da API do Spotify ocorreu.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

    print("\nPrograma finalizado.")
    sys.exit(0)

if __name__ == '__main__':
    PORT = 8888
    
    print(f"Para iniciar a autenticação, acesse: {REDIRECT_URI}")
    print(f"Certifique-se de que {REDIRECT_URI} está registrado no seu Dashboard de Desenvolvedor Spotify.")
    print("O navegador abrirá automaticamente ou você terá um link para clicar.")
    print("Após a autenticação, volte para este terminal para continuar.")

    try:
        app.run(host='127.0.0.1', port=PORT, debug=False, use_reloader=False)
    except SystemExit:
        pass
    except Exception as e:
        print(f"Erro ao iniciar o servidor Flask: {e}")
        sys.exit(1)

    if sp:
        main_cli_loop()
    else:
        print("Falha na autenticação. Não foi possível iniciar o organizador de playlists.")
        sys.exit(1)