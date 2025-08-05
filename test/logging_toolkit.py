"""
logging_toolkit - Biblioteca de utilidades para configuração e gerenciamento de logs

Este módulo fornece funções e classes para configurar logs em diferentes ambientes e casos de uso:

- Logs coloridos para terminal
- Logs para arquivos com rotação (por tempo ou tamanho)
- Configurações personalizadas para diferentes níveis de verbosidade
- Formatadores em texto ou JSON, compatíveis com análise em ferramentas externas
- Utilitários para temporização de operações e coleta de métricas customizadas
- **Funções utilitárias para logging de DataFrames PySpark** (ex: contagem de linhas, schema, amostras e estatísticas básicas)

Principais componentes:
-----------------------
- `ColoredFormatter`: Saída colorida no terminal para rápida identificação de níveis de log
- `JSONFormatter`: Logs em formato JSON para integração com ferramentas externas
- Funções para criação de handlers (console, arquivo, rotação por tempo ou tamanho)
- `LogTimer`: Medição de tempo de execução de blocos de código (context manager ou decorador)
- `LogMetrics`: Coleta e logging de métricas customizadas (contadores, timers, valores)
- **`log_spark_dataframe_info`: Logging fácil e estruturado de DataFrames PySpark**

Este toolkit é recomendado para instrumentação de pipelines de dados, ETLs e projetos onde rastreabilidade, auditabilidade e performance de logs são requisitos importantes.

"""

# --- Bibliotecas padrão do Python (sistema) ---
import os
import sys
import time
from datetime import datetime

# --- Logging (nativo do Python) ---
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# --- Tipagem (módulo padrão typing) ---
from typing import Dict, List, Optional, Union, Any, Tuple

# --- Bibliotecas de terceiros ---
import pytz

def _make_timezone_converter(tz_name: str):
    tz = pytz.timezone(tz_name)

    def converter(timestamp):
        # timestamp é um float (epoch)
        dt = datetime.fromtimestamp(timestamp, tz)
        return dt.timetuple()

    return converter

# Constantes de cores ANSI
class Colors:
    """Cores ANSI para formatação no terminal"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # Cores de texto
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Cores de fundo
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class ColoredFormatter(logging.Formatter):
    """
    Formatador personalizado que adiciona cores ao output de log no terminal
    
    Cores por nível:
    - DEBUG: Ciano
    - INFO: Verde
    - WARNING: Amarelo
    - ERROR: Vermelho
    - CRITICAL: Fundo vermelho com texto branco
    """
    
    # Mapeamento de níveis de log para cores
    COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BG_RED + Colors.WHITE + Colors.BOLD
    }

    def __init__(self, fmt: str = None, datefmt: str = None, style: str = '%', use_colors: bool = True):
        """
        Inicializa o formatador com suporte a cores
        
        Args:
            fmt: String de formato para logs
            datefmt: String de formato para data/hora
            style: Estilo de formatação ('%', '{' ou '$')
            use_colors: Se deve usar cores ANSI (desativar para ambientes que não suportam)
        """
        if fmt is None:
            fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        if datefmt is None:
            datefmt = "%Y-%m-%d %H:%M:%S"
            
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """
        Formata o registro de log com cores apropriadas
        
        Args:
            record: Registro de log a ser formatado
            
        Returns:
            Mensagem de log formatada com cores (se ativado)
        """
        # Salva os atributos originais que vamos modificar
        original_levelname = record.levelname
        original_msg = record.msg
        
        # Adiciona cores se ativado
        if self.use_colors:
            # Adiciona cor ao nível do log
            color = self.COLORS.get(record.levelno, Colors.RESET)
            record.levelname = f"{color}{record.levelname}{Colors.RESET}"
            
            # Adiciona cor à mensagem para erros e críticos
            if record.levelno >= logging.ERROR:
                record.msg = f"{color}{record.msg}{Colors.RESET}"
        
        # Formata a mensagem
        formatted_message = super().format(record)
        
        # Restaura os atributos originais
        record.levelname = original_levelname
        record.msg = original_msg
        
        return formatted_message


class JSONFormatter(logging.Formatter):
    """
    Formatador que gera logs em formato JSON para integração com ferramentas de análise de logs
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata um registro de log como JSON
        
        Args:
            record: Registro de log a ser formatado
            
        Returns:
            String JSON com os dados do log
        """
        import json
        
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Adiciona informações de exceção se houver
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Adiciona dados extras do LogRecord
        for key, value in record.__dict__.items():
            if key not in {
                "args", "asctime", "created", "exc_info", "exc_text", "filename",
                "funcName", "id", "levelname", "levelno", "lineno", "module", 
                "msecs", "message", "msg", "name", "pathname", "process",
                "processName", "relativeCreated", "stack_info", "thread", "threadName"
            }:
                log_data[key] = value
        
        return json.dumps(log_data)


def create_file_handler(
    log_file: str, 
    max_bytes: int = 10485760, 
    backup_count: int = 5,
    encoding: str = 'utf-8',
    formatter: logging.Formatter = None,
    level: int = logging.DEBUG
) -> logging.Handler:
    """
    Cria um handler de arquivo com rotação por tamanho
    
    Args:
        log_file: Caminho para o arquivo de log
        max_bytes: Tamanho máximo do arquivo antes de rotacionar (default: 10MB)
        backup_count: Número de arquivos de backup a manter
        encoding: Codificação do arquivo de log
        formatter: Formatador personalizado (opcional)
        level: Nível mínimo de log
        
    Returns:
        Handler configurado para arquivos com rotação
    """
    # Cria o diretório se não existir
    os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
    
    # Cria o handler com rotação
    handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes, 
        backupCount=backup_count,
        encoding=encoding
    )
    
    # Define o nível e formatador
    handler.setLevel(level)
    
    if formatter is None:
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    return handler


def create_timed_file_handler(
    log_file: str,
    when: str = 'midnight',
    interval: int = 1,
    backup_count: int = 7,
    encoding: str = 'utf-8',
    formatter: logging.Formatter = None,
    level: int = logging.DEBUG
) -> logging.Handler:
    """
    Cria um handler de arquivo com rotação por tempo
    
    Args:
        log_file: Caminho para o arquivo de log
        when: Quando fazer rotação ('S', 'M', 'H', 'D', 'W0'-'W6', 'midnight')
        interval: Intervalo de rotação
        backup_count: Número de arquivos de backup a manter
        encoding: Codificação do arquivo de log
        formatter: Formatador personalizado (opcional)
        level: Nível mínimo de log
        
    Returns:
        Handler configurado para arquivos com rotação por tempo
    """
    # Cria o diretório se não existir
    os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
    
    # Cria o handler com rotação baseada em tempo
    handler = TimedRotatingFileHandler(
        log_file,
        when=when,
        interval=interval,
        backupCount=backup_count,
        encoding=encoding
    )
    
    # Define o nível e formatador
    handler.setLevel(level)
    
    if formatter is None:
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    return handler


def create_console_handler(
    level: int = logging.INFO,
    use_colors: bool = True,
    formatter: logging.Formatter = None
) -> logging.Handler:
    """
    Cria um handler para console (stdout) com suporte a cores
    
    Args:
        level: Nível mínimo de log
        use_colors: Se deve usar formatação colorida
        formatter: Formatador personalizado (opcional)
        
    Returns:
        Handler configurado para console
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    if formatter is None:
        formatter = ColoredFormatter(use_colors=use_colors)
    
    handler.setFormatter(formatter)
    return handler


def configure_basic_logging(
    level: int = logging.INFO,
    log_format: str = '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    date_format: str = '%Y-%m-%d %H:%M:%S',
    use_colors: bool = True
) -> None:
    """
    Configura logging básico para console com formatação colorida
    
    Args:
        level: Nível de log padrão
        log_format: Formato das mensagens de log
        date_format: Formato da data/hora nos logs
        use_colors: Se deve usar cores no console
    """
    # Remove handlers existentes para evitar duplicação
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configura o logger raiz
    root_logger.setLevel(level)
    
    # Adiciona handler para console
    console_handler = create_console_handler(level=level, use_colors=use_colors)
    if use_colors:
        console_handler.setFormatter(ColoredFormatter(fmt=log_format, datefmt=date_format, use_colors=use_colors))
    else:
        console_handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))
    
    root_logger.addHandler(console_handler)

    return root_logger


def get_logger(
    name: str,
    level: Optional[int] = None,
    handlers: Optional[List[logging.Handler]] = None,
    propagate: Optional[bool] = None,
    caplog_friendly: bool = False,
) -> logging.Logger:
    """
    Cria ou obtém um logger com configuração flexível para produção e testes com caplog.

    Args:
        name (str): Nome do logger.
        level (int, optional): Nível de log. Se None, usa o nível padrão.
        handlers (List[logging.Handler], optional): Handlers a adicionar ao logger.
        propagate (bool, optional): Se None, define automaticamente conforme caplog_friendly.
        caplog_friendly (bool): Se True, não adiciona handlers e ativa propagate (para testes pytest caplog).

    Returns:
        logging.Logger: Logger configurado.
    """
    logger = logging.getLogger(name)

    # Determina propagate automaticamente se não especificado
    if propagate is None:
        propagate = caplog_friendly

    # Configura nível
    if level is not None:
        logger.setLevel(level)

    # Configuração caplog-friendly
    if caplog_friendly:
        # Remove handlers próprios (para não “bloquear” o caplog)
        for h in logger.handlers[:]:
            logger.removeHandler(h)
        logger.propagate = True  # logs vão para o root logger
    else:
        # Produção: pode ter handlers customizados e controlar propagate
        if handlers:
            for h in logger.handlers[:]:
                logger.removeHandler(h)
            for h in handlers:
                logger.addHandler(h)
        logger.propagate = propagate

    return logger


def setup_file_logging(
    logger_name: str,
    log_folder: str = "desconhecidos/",
    log_dir: str = "/dbfs/mnt/logs/",
    file_prefix: str = None,
    level: int = logging.DEBUG,
    console_level: int = logging.INFO,
    rotation: str = 'time',
    max_bytes: int = 10485760,
    backup_count: int = 5,
    add_console: bool = True,
    use_colors: bool = True,
    log_format: str = '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    date_format: str = '%Y-%m-%d %H:%M:%S',
    utc: str = 'America/Sao_Paulo',
    json_format: bool = False, 
) -> logging.Logger:
    """
    Configura um logger com saída para arquivo com rotação e console.

    Args:
        logger_name: Nome do logger
        log_folder: Subpasta para salvar os logs
        file_prefix: Prefixo do arquivo
        level: Nível de log para o arquivo
        console_level: Nível de log para o console
        rotation: 'time' ou 'size'
        max_bytes: Para rotação por tamanho
        backup_count: Número de arquivos de backup
        add_console: Adicionar handler de console
        use_colors: Usar cores no console
        log_format: Formato de log (quando não usa JSON)
        date_format: Formato da data/hora
        utc: Timezone a ser aplicado
        json_format: Se True, usa JSONFormatter para arquivo e console
    """
    # Cria o diretório
    log_dir = f"{log_dir}{log_folder}"
    os.makedirs(log_dir, exist_ok=True)

    # Nome do arquivo
    if file_prefix is None:
        file_prefix = logger_name.replace(".", "_")

    utc_tz = pytz.timezone(utc)
    timestamp = datetime.now(utc_tz).strftime("%Y%m%d_%H:%M:%S")
    
    extension = "json" if json_format else "log"
    log_file = os.path.join(log_dir, f"{timestamp}-{file_prefix}.{extension}")


    # Escolhe formatter
    if json_format:
        file_formatter = JSONFormatter()
    else:
        file_formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
        file_formatter.converter = _make_timezone_converter(utc)

    handlers = []

    # Handler de arquivo
    if rotation.lower() == 'time':
        file_handler = create_timed_file_handler(
            log_file=log_file,
            level=level,
            formatter=file_formatter,
            backup_count=backup_count,
        )
    else:
        file_handler = create_file_handler(
            log_file=log_file,
            max_bytes=max_bytes,
            backup_count=backup_count,
            level=level,
            formatter=file_formatter,
        )
    handlers.append(file_handler)

    # Handler de console
    if add_console:
        if json_format:
            console_formatter = JSONFormatter()
        else:
            console_formatter = ColoredFormatter(fmt=log_format, datefmt=date_format, use_colors=use_colors)
            console_formatter.converter = _make_timezone_converter(utc)

        console_handler = create_console_handler(
            level=console_level,
            use_colors=use_colors,
            formatter=console_formatter,
        )
        handlers.append(console_handler)

    # Cria o logger
    logger = get_logger(logger_name, level=level, handlers=handlers, propagate=False)

    logger.info(f"Logger configurado: json_format={json_format}")

    # Método para fechar handlers
    def close():
        for handler in logger.handlers[:]:
            try:
                handler.flush()
                handler.close()
            except Exception as e:
                print(f"Erro ao fechar handler: {e}")
            logger.removeHandler(handler)

    logger.close = close

    return logger

class LogTimer:
    """
    Utilitário para medir e logar tempo de execução de operações
    
    Pode ser usado como context manager:
    ```
    with LogTimer(logger, "Operação de processamento"):
        # código a ser medido
    ```
    
    Ou como decorador:
    ```
    @LogTimer.as_decorator(logger, "Função de transformação")
    def minha_funcao():
        # código a ser medido
    ```
    """
    
    def __init__(self, logger: logging.Logger, operation_name: str, level: int = logging.INFO):
        """
        Inicializa o timer de log
        
        Args:
            logger: Logger para mensagens
            operation_name: Nome da operação sendo cronometrada
            level: Nível de log para mensagens
        """
        self.logger = logger
        self.operation_name = operation_name
        self.level = level
        self.start_time = None
        
    def __enter__(self):
        """Inicia a contagem de tempo ao entrar no contexto"""
        self.start_time = time.time()
        self.logger.log(self.level, f"Iniciando: {self.operation_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Registra o tempo ao sair do contexto"""
        end_time = time.time()
        elapsed = end_time - self.start_time
        
        if exc_type is not None:
            # Se houve exceção
            self.logger.error(
                f"Falha em '{self.operation_name}' após {elapsed:.2f} segundos. "
                f"Erro: {exc_type.__name__}: {str(exc_val)}"
            )
        else:
            # Operação bem-sucedida
            self.logger.log(
                self.level, 
                f"Concluído: {self.operation_name} em {elapsed:.2f} segundos."
            )
    
    @staticmethod
    def as_decorator(logger: logging.Logger, operation_name: str = None, level: int = logging.INFO):
        """
        Cria um decorador para medir tempo de execução de funções
        
        Args:
            logger: Logger para mensagens
            operation_name: Nome da operação (se None, usa o nome da função)
            level: Nível de log para mensagens
            
        Returns:
            Decorador para função
        """
        def decorator(func):
            import functools
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                op_name = operation_name if operation_name is not None else func.__name__
                with LogTimer(logger, op_name, level):
                    return func(*args, **kwargs)
            return wrapper
        return decorator

def log_spark_dataframe_info(
    df,
    logger: logging.Logger,
    name: str = "DataFrame",
    show_schema: bool = True,
    show_sample: bool = False,
    sample_rows: int = 5,
    log_level: int = logging.INFO,
):
    """
    Loga informações resumidas sobre um DataFrame PySpark usando o logger fornecido.

    Args:
        df (pyspark.sql.DataFrame): DataFrame a ser logado.
        logger (logging.Logger): Logger para registrar as informações.
        name (str): Nome de referência do DataFrame (usado nos logs).
        show_schema (bool): Se True, loga o schema do DataFrame.
        show_sample (bool): Se True, loga uma amostra dos dados.
        sample_rows (int): Número de linhas a mostrar na amostra.
        log_level (int): Nível de log a ser utilizado.

    Exemplo:
        log_spark_dataframe_info(df, logger, name="BronzeLayer", show_schema=True)
    """
    if df is None:
        logger.warning(f"[{name}] DataFrame é None.")
        return

    try:
        row_count = df.count()
        logger.log(log_level, f"[{name}] Número de linhas: {row_count}")
    except Exception as e:
        logger.error(f"[{name}] Erro ao contar linhas: {e}")

    if show_schema:
        try:
            schema_str = df._jdf.schema().treeString()
            logger.log(log_level, f"[{name}] Schema:\n{schema_str}")
        except Exception as e:
            logger.error(f"[{name}] Erro ao mostrar schema: {e}")

    if show_sample:
        try:
            sample_data = df.limit(sample_rows).toPandas()
            logger.log(log_level, f"[{name}] Amostra ({sample_rows} linhas):\n{sample_data}")
        except Exception as e:
            logger.error(f"[{name}] Erro ao exibir amostra: {e}")

    # Estatísticas básicas
    try:
        cols = df.columns
        stats_cols = [c for c, t in df.dtypes if t in ["int", "bigint", "double", "float", "decimal", "long"]]
        if stats_cols:
            stats = df.select(*stats_cols).describe().toPandas()
            logger.log(log_level, f"[{name}] Estatísticas:\n{stats}")
    except Exception as e:
        logger.error(f"[{name}] Erro ao calcular estatísticas: {e}")


class LogMetrics:
    """
    Classe utilitária para coletar e logar métricas de processamento
    
    Exemplo:
    ```
    metrics = LogMetrics(logger)
    metrics.start('processamento_total')
    
    metrics.increment('registros_processados')
    metrics.increment('registros_processados')
    metrics.increment('erros', 1)
    
    metrics.set('tamanho_lote', 1000)
    
    metrics.stop('processamento_total')
    metrics.log_all()
    ```
    """
    
    def __init__(self, logger: logging.Logger, level: int = logging.INFO):
        """
        Inicializa o coletor de métricas
        
        Args:
            logger: Logger para registrar métricas
            level: Nível de log para métricas
        """
        self.logger = logger
        self.level = level
        self.counters = {}
        self.values = {}
        self.timers = {}
        
    def increment(self, metric_name: str, value: int = 1):
        """
        Incrementa um contador de métrica
        
        Args:
            metric_name: Nome da métrica
            value: Valor a incrementar (default: 1)
        """
        if metric_name not in self.counters:
            self.counters[metric_name] = 0
        self.counters[metric_name] += value
        
    def set(self, metric_name: str, value: Any):
        """
        Define um valor para uma métrica
        
        Args:
            metric_name: Nome da métrica
            value: Valor a definir
        """
        self.values[metric_name] = value
        
    def start(self, timer_name: str):
        """
        Inicia um timer para medir tempo de operação
        
        Args:
            timer_name: Nome do timer
        """
        self.timers[timer_name] = {'start': time.time(), 'elapsed': None}
        
    def stop(self, timer_name: str) -> float:
        """
        Para um timer e calcula o tempo decorrido
        
        Args:
            timer_name: Nome do timer
            
        Returns:
            Tempo decorrido em segundos
        """
        if timer_name in self.timers and 'start' in self.timers[timer_name]:
            elapsed = time.time() - self.timers[timer_name]['start']
            self.timers[timer_name]['elapsed'] = elapsed
            return elapsed
        return 0.0
        
    def log(self, metric_name: str, value: Any = None):
        """
        Loga uma métrica específica
        
        Args:
            metric_name: Nome da métrica
            value: Valor opcional para sobrescrever
        """
        if value is not None:
            self.logger.log(self.level, f"Métrica '{metric_name}': {value}")
            return
            
        if metric_name in self.counters:
            self.logger.log(self.level, f"Contador '{metric_name}': {self.counters[metric_name]}")
        elif metric_name in self.values:
            self.logger.log(self.level, f"Valor '{metric_name}': {self.values[metric_name]}")
        elif metric_name in self.timers and self.timers[metric_name].get('elapsed') is not None:
            elapsed = self.timers[metric_name]['elapsed']
            self.logger.log(self.level, f"Timer '{metric_name}': {elapsed:.2f} segundos")
            
    def log_all(self):
        """
        Loga todas as métricas coletadas
        """
        self.logger.log(self.level, "--- Métricas de Processamento ---")
        
        # Loga contadores
        if self.counters:
            self.logger.log(self.level, "Contadores:")
            for name, value in self.counters.items():
                self.logger.log(self.level, f"  - {name}: {value}")
                
        # Loga valores
        if self.values:
            self.logger.log(self.level, "Valores:")
            for name, value in self.values.items():
                self.logger.log(self.level, f"  - {name}: {value}")
                
        # Loga timers
        active_timers = []
        completed_timers = []
        
        for name, timer in self.timers.items():
            if timer.get('elapsed') is not None:
                completed_timers.append((name, timer['elapsed']))
            else:
                # Timer ainda ativo
                current = time.time() - timer['start']
                active_timers.append((name, current))
                
        if completed_timers:
            self.logger.log(self.level, "Timers concluídos:")
            for name, elapsed in completed_timers:
                self.logger.log(self.level, f"  - {name}: {elapsed:.2f} segundos")
                
        if active_timers:
            self.logger.log(self.level, "Timers ativos:")
            for name, current in active_timers:
                self.logger.log(self.level, f"  - {name}: {current:.2f} segundos (em execução)")
                
        self.logger.log(self.level, "--------------------------------")
