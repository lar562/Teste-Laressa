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
    Wait For Elements State    input[placeholder="ex.: exemplo@mail.com"]    visible

Preencher email e senha válidos
    Fill Text    input[placeholder="ex.: exemplo@mail.com"]    ${EMAIL}
    Fill Text    input[placeholder="adicione sua senha"]       ${SENHA}
    Click        button:has-text("entrar")
    Wait For Navigation

Deve ser redirecionado para a home
    Get Url    matches    ^https://www\\.americanas\\.com\\.br/?$
