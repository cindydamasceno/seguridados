# SOBRE A SEGURIDADOS

A SEGURIDADOS é uma proposta para ampliar o acesso a dados abertos sobre Crimes Violentos Letais Intencionais (CVLI) no Ceará. Este protótipo tem como base as divulgações mensais da Secretaria da Segurança Pública e Defesa Social do Estado do Ceará (SSPDS-CE).

Utilizando técnicas de automação, um robô captura todo dia 10 as informações atualizadas dos indicadores FEMINICÍDIO, HOMICÍDIO DOLOSO, LATROCÍNIO e LESÃO CORPORAL SEGUIDO DE MORTE. Estes dados são processados e podem ser acessados no formulário do tópico anterior ou via solicitações API.

ATENÇÃO: ESTA FERRAMENTA É UM PROTÓTIPO E DEVE SER LIDA COM CAUTELA. ENTRE EM CONTATO COM A RESPONSÁVEL AO ENCONTRAR DIVERGÊNCIAS
<hr>

## DICIONÁRIO DE DADOS

| VALOR | COMO LER | DETALHES |
|-------|----------|----------|
| `Ano` | Ano da ocorrência | A partir de 01/01/2009 |
| `Regiao` | Região administrativa do município da ocorrência | De acordo com limitação do Instituto de Pesquisa e Estratégia Econômica do Ceará (IPECE) |
| `CdRegiao` | Identificação da Região Administrativa na API |  1-Cariri / 2-Centro Sul / 3-Grande Fortaleza / 4-Litoral Leste / 5-Litoral Norte / 6-Litoral Oeste / Vale do Curu / 7-Maciço de Baturité / 8-Serra da Ibiapaba / 9-Sertão Central / 10-Sertão de Canindé / 11-Sertão de Sobral / 12-Sertão dos Crateús / 13-Sertão dos Inhamuns / 14-Vale do Jaguaribe |
| `CdIbge` | Código do IBGE de cada município | [Confira listagem do IBGE dos códigos de cada município](https://www.ibge.gov.br/explica/codigos-dos-municipios.php) |
| `Município` | Nome do município cearense | Nome do município cearense |
| `AIS` | Áreas Integradas de Segurança – Divisão territorial da SSPDS-CE | [Confira lista de AIS no portal da SSPDS-CE](https://www.sspds.ce.gov.br/ais/) |
| `Natureza` | Natureza do Crime Violento Letal Intecional (CVLI) | Feminicídio, Homicídio Doloso, Lesão corporal seguida de morte, Roubo seguido de morte |
| `CdIndicador` | Identificação da natureza do Crime Violento Letal Intecional (CVLI) na API | 1-FEMINICÍDIO / 2-HOMICIDIO DOLOSO / 3-LESAO CORPORAL SEGUIDA DE MORTE / 4-ROUBO SEGUIDO DE MORTE (LATROCINIO) |
| `Data` | Data da ocorrência | Data da ocorrência |
| `Hora` | Hora da ocorrência | Hora da ocorrência |
| `Dia da Semana` | Dia da ocorrência | Dia da ocorrência |
| `Meio Empregado` | Tipo de arma utilizada na ocorrência | Arma de fogo, Arma branca, Outros meios, meio não informado |
| `Gênero` | Gênero da vítima | Feminino, Masculino, Não informado |
| `Idade da Vítima` | Idade da Vítima | #NULL: Valor não disponibilizado pela SSPDS-CE |
| `Escolaridade da Vítima` | Escolaridade da Vítima | Não informada/ Alfabetizado/ Ensino Fundamental Completo/ Ensino Fundamental Incompleto/ Ensino Médio Completo/ Ensino Médio Incompleto/ Não Alfabetizado/ Superior Completo/ Superior Incompleto |
| `Raça da Vítima` | Raça da Vítima | Amarela, Branca, Indígena, Não informada, Parda, Preta |
