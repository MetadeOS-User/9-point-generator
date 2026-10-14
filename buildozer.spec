[app]

# Nome exibido embaixo do ícone no celular
title = Padrao 9 Pontos

# Identificador do app = domain + name. Troque "exemplo" pelo seu nome/usuário.
package.name = padrao9pontos
package.domain = org.exemplo

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = bin, .github, .buildozer

version = 1.0

# O Buildozer escolhe a versão do Kivy compatível com o python-for-android.
requirements = python3,kivy

orientation = portrait
fullscreen = 0

# O app não precisa de nenhuma permissão.
android.permissions =

# Remova armeabi-v7a para build mais rápido (só celulares 64 bits).
android.archs = arm64-v8a, armeabi-v7a

# Necessário para builds sem interação (GitHub Actions).
android.accept_sdk_license = True

# Para trocar o ícone, coloque um PNG 512x512 na pasta e descomente:
# icon.filename = %(source.dir)s/icone.png

[buildozer]

log_level = 2
warn_on_root = 1
