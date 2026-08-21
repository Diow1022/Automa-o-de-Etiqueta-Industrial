# Automa-o-de-Etiqueta-Industrial
Programa Criado para automatizar etiquetas para serviços executados
##  Sistema de Automação e Impressão de Etiquetas

Este projeto consiste em um sistema desenvolvido em **Python** para automatizar o processo de geração e impressão de etiquetas a partir de informações cadastradas de forma dinâmica.

A solução foi desenvolvida com o objetivo de reduzir processos manuais, minimizar erros operacionais e tornar o fluxo de preparação e impressão de etiquetas mais rápido, organizado e intuitivo.

###  Funcionamento do sistema

O sistema utiliza uma arquitetura de integração entre diferentes ferramentas para permitir que os dados sejam inseridos de maneira simples pelo usuário e posteriormente processados automaticamente pelo programa.

As informações podem ser cadastradas por meio de **formulários**, sendo armazenadas em uma **planilha do Google Sheets**. Dessa forma, o usuário não precisa interagir diretamente com o código ou com estruturas técnicas do sistema.

Após o cadastro das informações, o programa desenvolvido em Python realiza a leitura dos dados disponíveis, processa as informações e gera automaticamente as etiquetas prontas para impressão.

###  Tecnologias utilizadas

* **Python** — Desenvolvimento da lógica principal do sistema.
* **Tkinter** — Interface gráfica para configuração e interação com o usuário.
* **Google Sheets API** — Integração com planilhas para armazenamento e gerenciamento das informações.
* **Google Forms** — Possibilidade de cadastro de pedidos e informações de forma simples e intuitiva.
* **ReportLab** — Geração dinâmica das etiquetas em formato PDF.
* **QRCode** — Geração de códigos QR contendo informações relacionadas aos pedidos.
* **Google Drive** — Utilização como suporte para armazenamento e integração de arquivos e serviços.
* **PyInstaller** — Empacotamento da aplicação Python em um arquivo executável para facilitar sua utilização.

###  Fluxo de funcionamento

1. O usuário preenche um formulário com as informações do pedido.
2. Os dados são enviados automaticamente para uma planilha no **Google Sheets**.
3. O sistema desenvolvido em Python monitora e consulta as informações disponíveis.
4. Novos registros são identificados e processados automaticamente.
5. O programa gera uma etiqueta personalizada contendo informações como:

   * Número do pedido;
   * Vendedor;
   * Produto;
   * Valor;
   * Status de embalagem e conferência;
   * Código QR com informações do pedido.
6. A etiqueta é gerada em formato **PDF** e enviada para impressão.

###  Visão técnica

O projeto utiliza uma abordagem de automação baseada na integração entre ferramentas externas e uma aplicação local desenvolvida em Python.

O **Google Sheets** atua como uma camada intermediária para armazenamento e organização dos dados, permitindo que diferentes usuários possam adicionar informações simultaneamente sem a necessidade de acesso direto ao sistema principal.

A utilização de formulários torna o processo de cadastro mais acessível e intuitivo, enquanto a aplicação em Python é responsável pelo processamento dos dados, geração dos arquivos e automação da impressão.

Essa arquitetura permite que o sistema seja facilmente adaptado para diferentes cenários, como:

* Controle de pedidos;
* Etiquetagem de produtos;
* Logística;
* Separação de mercadorias;
* Controle de estoque;
* Automação de processos administrativos.

###  Objetivo do projeto

O principal objetivo é demonstrar como ferramentas acessíveis, como **Python, Google Sheets e formulários**, podem ser integradas para criar uma solução de automação prática e funcional.

Além de automatizar a impressão de etiquetas, o projeto busca oferecer uma experiência simples para o usuário final, separando a complexidade técnica do processo operacional.

Dessa forma, o usuário interage apenas com interfaces intuitivas, enquanto o sistema realiza automaticamente o processamento, geração e impressão das etiquetas em segundo plano.
