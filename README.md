# Detector
Karel Prog


PROGRAM TCPSERV_PARSE
%NOLOCKGROUP
%NOPAUSE = ERROR + COMMAND + TPENABLE
%ENVIRONMENT flbt      -- Para funções de socket
%ENVIRONMENT strng     -- Para funções de string (INDEX, STR_LEN)
%ENVIRONMENT regope    -- Para operações com registradores (SET_REAL_REG)

-----------------------------------------------------------------------
-- Declaração de Variáveis
-----------------------------------------------------------------------
VAR
  -- Variáveis do Socket
  client_file     : FILE
  incoming_msg    : STRING[128]
  response_msg    : STRING[128]
  status          : INTEGER
  is_connected    : BOOLEAN

  -- Variáveis para as coordenadas decodificadas
  x_coord         : REAL
  y_coord         : REAL
  z_rot           : REAL
  w_rot           : REAL

-----------------------------------------------------------------------
-- ROTINA: parse_message
-- Objetivo: Decodificar a string de entrada (formato "X,Y,Z,W") e
--           popular as variáveis de coordenadas.
-- Retorna: BOOLEAN - TRUE se o parsing for bem-sucedido, FALSE se houver erro.
-----------------------------------------------------------------------
ROUTINE parse_message(message: STRING; x, y, z, w: REAL): BOOLEAN
  VAR
    -- Variáveis locais para o parsing
    temp_str        : STRING[32]
    work_str        : STRING[128] -- String de trabalho que será modificada
    delim_pos       : INTEGER
  BEGIN
    work_str = message

    -- 1. Extrair Coordenada X
    delim_pos = INDEX(work_str, ',')
    IF delim_pos > 0 THEN
      temp_str = SUB_STR(work_str, 1, delim_pos - 1)
      CNV_STR_REAL(temp_str, x)
      work_str = SUB_STR(work_str, delim_pos + 1, STR_LEN(work_str))
    ELSE
      WRITE('ERRO: Formato invalido (faltando Y,Z,W)!', CR)
      RETURN(FALSE)
    ENDIF

    -- 2. Extrair Coordenada Y
    delim_pos = INDEX(work_str, ',')
    IF delim_pos > 0 THEN
      temp_str = SUB_STR(work_str, 1, delim_pos - 1)
      CNV_STR_REAL(temp_str, y)
      work_str = SUB_STR(work_str, delim_pos + 1, STR_LEN(work_str))
    ELSE
      WRITE('ERRO: Formato invalido (faltando Z,W)!', CR)
      RETURN(FALSE)
    ENDIF

    -- 3. Extrair Rotação Z
    delim_pos = INDEX(work_str, ',')
    IF delim_pos > 0 THEN
      temp_str = SUB_STR(work_str, 1, delim_pos - 1)
      CNV_STR_REAL(temp_str, z)
      work_str = SUB_STR(work_str, delim_pos + 1, STR_LEN(work_str))
    ELSE
      WRITE('ERRO: Formato invalido (faltando W)!', CR)
      RETURN(FALSE)
    ENDIF

    -- 4. Extrair Rotação W (o que sobrou da string)
    temp_str = work_str
    CNV_STR_REAL(temp_str, w)

    RETURN(TRUE)

  END parse_message

-----------------------------------------------------------------------
-- PROGRAMA PRINCIPAL
-----------------------------------------------------------------------
BEGIN
  -- Define a porta do servidor
  SET_VAR(0, '*SYSTEM*', '$HOSTS_CFG[3].$SERVER_PORT', 59022, status)

  -- Loop principal do servidor para aceitar múltiplas conexões
  REPEAT
    is_connected = FALSE
    WRITE('Aguardando conexao do cliente...', CR)

    -- Aguarda por uma conexão na Tag de Servidor 'S3:'
    MSG_CONNECT('S3:', status)

    IF status = 0 THEN
      is_connected = TRUE
      WRITE('Cliente conectado!', CR)

      OPEN FILE client_file('RW', 'S3:')
      status = IO_STATUS(client_file)

      IF status = 0 THEN
        -- Loop para receber e processar mensagens
        REPEAT
          WRITE('Aguardando mensagem do Python...', CR)
          READ client_file(incoming_msg)
          status = IO_STATUS(client_file)

          IF status = 0 THEN
            WRITE('Python disse: ', incoming_msg, CR)

            -- Chama a rotina de parsing para decodificar a mensagem
            IF parse_message(incoming_msg, x_coord, y_coord, z_rot, w_rot) THEN
              -- ** INÍCIO DA LÓGICA DE GRAVAÇÃO NOS REGISTRADORES **
              WRITE('Gravando valores nos registradores...', CR)
              SET_REAL_REG(1, x_coord, status)
              IF status <> 0 THEN
                WRITE('Erro ao gravar R[1]!', CR)
              ENDIF
              
              SET_REAL_REG(2, y_coord, status)
              IF status <> 0 THEN
                WRITE('Erro ao gravar R[2]!', CR)
              ENDIF

              SET_REAL_REG(3, z_rot, status)
              IF status <> 0 THEN
                WRITE('Erro ao gravar R[3]!', CR)
              ENDIF

              SET_REAL_REG(4, w_rot, status)
              IF status <> 0 THEN
                WRITE('Erro ao gravar R[4]!', CR)
              ENDIF
              
              WRITE('Valores gravados em R[1] a R[4].', CR)
              -- ** FIM DA LÓGICA DE GRAVAÇÃO **

              -- Prepara e envia uma resposta de sucesso
              response_msg = 'KAREL: OK, Registradores gravados.'
              WRITE client_file(response_msg, CR)
            ELSE
              -- Prepara e envia uma resposta de erro
              response_msg = 'KAREL: ERRO DE FORMATO'
              WRITE client_file(response_msg, CR)
            ENDIF
          ENDIF

        UNTIL status <> 0

        WRITE('Fechando arquivo do cliente.', CR)
        CLOSE FILE client_file
      ELSE
        WRITE('Erro ao abrir a Tag S3 como arquivo. Status: ', status, CR)
      ENDIF

      WRITE('Desconectando cliente...', CR)
      MSG_DISCO('S3:', status)
    ELSE
      WRITE('Falha na conexao. Status: ', status, CR)
      DELAY 2000
    ENDIF

  UNTIL FALSE

END TCPSERV_PARSE
