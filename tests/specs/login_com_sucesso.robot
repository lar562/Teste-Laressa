*** Settings ***
Library     Browser


*** Test Cases ***
1: Login com sucesso
    [Tags]    trello-6a3bbe923eeb1e06f9280bea
    Que o usuário está na tela de login
    Preencher email e senha válidos
    Deve ser redirecionado para a home


*** Keywords ***
# Implemente aqui as keywords referenciadas nos test cases acima.
