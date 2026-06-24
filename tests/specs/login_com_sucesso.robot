*** Settings ***
Library    Browser

*** Variables ***
${URL_LOGIN}      https://www.americanas.com.br/login
${EMAIL}          %{TEST_EMAIL}
${SENHA}          %{TEST_PASSWORD}

*** Test Cases ***
Login com sucesso
    [Tags]    trello-uEoNqYtf
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

Deve ser redirecionado para a home
    Wait For Elements State    css=body    visible    timeout=15s
    ${url}=    Get Url
    Should Match Regexp    ${url}    ^https://www\\.americanas\\.com\\.br
