*** Settings ***
Library    Browser

*** Variables ***
${URL_LOGIN}      https://www.americanas.com.br/login
${EMAIL}          %{TEST_EMAIL}
${SENHA}          %{TEST_PASSWORD}

*** Test Cases ***
Login com sucesso
    [Tags]    trello-login
    O usuário está na tela de login
    Preencher email e senha válidos
    Deve ser redirecionado para a home

*** Keywords ***
O usuário está na tela de login
    New Browser    chromium    headless=true
    New Page       ${URL_LOGIN}
    Wait For Elements State    text=entrar com email e senha    visible
    Click    text=entrar com email e senha
    Wait For Elements State    input[type="email"]    visible

Preencher email e senha válidos
    Fill Text    input[type="email"]      ${EMAIL}
    Fill Text    input[type="password"]   ${SENHA}
    Click        button:has-text("Entrar")
    Wait For Navigation

Deve ser redirecionado para a home
    Get Url    matches    ^https://www\\.americanas\\.com\\.br/?$
