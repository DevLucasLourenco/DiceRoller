# Dice Roller Arcano

Aplicacao Python para rolagem de dados de RPG de mesa com interface grafica, animacao cinematografica e historico na tela.

O visual usa uma identidade propria de fantasia medieval: fundo escuro, detalhes dourados, dado central em canvas, particulas simples, desaceleracao antes do resultado e destaque especial para resultado maximo ou minimo. Nao usa assets, marcas, sons, fontes ou interface de jogos proprietarios.

## Recursos

- Rolagem de D4, D5, D6, D8, D10, D12, D20, D50, D100 ou qualquer outro numero de lados.
- Modificador positivo, negativo ou zero.
- Nome opcional para a rolagem.
- Validacao amigavel de entradas.
- Animacao com numeros rapidos, giro, tremor, desaceleracao e revelacao final.
- Efeito dourado para resultado maximo.
- Efeito vermelho para resultado minimo.
- Historico das ultimas rolagens.
- Codigo separado em modulos de interface, logica, validacao, animacao e estilos.

## Estrutura

```text
dice_roller/
|
|-- main.py
|-- app/
|   |-- interface.py
|   |-- dice_engine.py
|   |-- animation.py
|   |-- validators.py
|   |-- styles.py
|
|-- assets/
|   |-- sounds/
|   |-- images/
|   |-- fonts/
|
|-- tests/
|   |-- test_dice_engine.py
|   |-- test_validators.py
|
|-- README.md
```

## Como executar

Use Python 3.10 ou superior.

```bash
python main.py
```

O projeto usa apenas bibliotecas da biblioteca padrao do Python (`tkinter`, `random`, `math` e afins).

## Como testar

```bash
python -B -m unittest discover -s tests -v
```

## Uso

1. Informe os lados do dado, como `20` ou `D20`.
2. Informe o modificador, como `+3`, `-2` ou `0`.
3. Escolha ou escreva o nome da rolagem.
4. Clique em `Rolar Dado`.

O resultado mostra o valor natural, modificador, total final e adiciona a rolagem ao historico.
