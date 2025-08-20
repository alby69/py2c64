# py2c64 - Python to Commodore 64 Compiler

Un compiler Python-to-6502 per Commodore 64 completamente riprogettato con principi Object-Oriented.

## 📋 Descrizione

py2c64 è un compiler che traduce codice Python in assembly 6502 ottimizzato per il Commodore 64. Il progetto è stato completamente riprogettato utilizzando principi di programmazione orientata agli oggetti per garantire modularità, estensibilità e maintainability.

## ✨ Caratteristiche Principali

### 🏗️ Architettura Moderna
- **Design Pattern Visitor**: Per la generazione del codice AST
- **Symbol Table Management**: Gestione completa di scope e variabili
- **Label Management**: Generazione automatica di label univoche
- **Assembly Output Management**: Organizzazione strutturata dell'output

### 🎯 Funzionalità Supportate
- **Tipi di Dati**: INT16, FLOAT32, STRING, VOID
- **Operazioni Aritmetiche**: +, -, *, /, %
- **Operazioni di Confronto**: ==, !=, <, >, <=, >=
- **Strutture di Controllo**: if/else, while, for (con range)
- **Funzioni**: Definizione e chiamata con parametri
- **Variabili**: Globali e locali con scope management

### 🎮 Funzionalità Hardware C64
- **Grafica**: Attivazione/disattivazione, clear screen, drawing primitives
- **Sprites**: Gestione completa degli sprite
- **Routine Ottimizzate**: Libreria di routine assembly per operazioni comuni

## 🏛️ Architettura del Sistema

### Componenti Principali

#### Core Types e Enums
```python
class DataType(Enum):
    INT16 = "int16"
    FLOAT32 = "float32"
    STRING = "string"
    VOID = "void"

class OperationType(Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    # ... altri operatori
```

#### Symbol Table Management
- **SymbolTable**: Gestione di variabili, funzioni e scope
- **Variable**: Rappresentazione delle variabili con tipo e scope
- **Function**: Rappresentazione delle funzioni con parametri e tipo di ritorno

#### Label Management
- **LabelManager**: Generazione automatica di label univoche
- Prevenzione di conflitti di nomi
- Tracking delle label utilizzate

#### Assembly Output Management
- **AssemblyOutput**: Organizzazione dell'output in sezioni
- Sezione dati, codice e routine separate
- Generazione strutturata dell'assembly finale

### Abstract Syntax Tree (AST)

#### Nodi Base
```python
class ASTNode(ABC):
    @abstractmethod
    def accept(self, visitor: 'CodeGenerator') -> Any:
        pass

class Expression(ASTNode):
    # Classe base per espressioni
    
class Statement(ASTNode):
    # Classe base per statement
```

#### Nodi Specifici
- **Literal**: Valori costanti
- **Identifier**: Riferimenti a variabili
- **BinaryOperation**: Operazioni binarie
- **FunctionCall**: Chiamate di funzione
- **Assignment**: Assegnazioni
- **IfStatement**: Controlli condizionali
- **WhileStatement**: Loop while
- **ForStatement**: Loop for
- **FunctionDefinition**: Definizioni di funzione
- **ReturnStatement**: Statement di ritorno

### Code Generation (Visitor Pattern)

#### CodeGenerator Astratto
```python
class CodeGenerator(ABC):
    def __init__(self, symbol_table: SymbolTable, 
                 label_manager: LabelManager, 
                 output: AssemblyOutput):
        # Inizializzazione componenti
```

#### C64CodeGenerator
Implementazione specifica per il Commodore 64:
- Generazione di codice 6502 ottimizzato
- Gestione delle routine hardware
- Operazioni aritmetiche a 16 bit
- Gestione dello stack per le funzioni

### Parser (Python AST → Internal AST)

#### PythonASTParser
- Converte l'AST Python nel nostro AST interno
- Supporta tutti i costrutti Python implementati
- Gestione degli errori di sintassi
- Inferenza dei tipi (semplificata)

### Hardware Libraries

#### C64HardwareLibrary
Routine specifiche per il Commodore 64:
- **Grafica**: Attivazione modalità bitmap, clear screen, drawing primitives
- **Sprites**: Gestione completa degli sprite
- **I/O**: Routine per input/output

### Funzioni Grafiche e Hardware

Il compilatore offre un'ampia gamma di funzioni per interagire con l'hardware del Commodore 64, in particolare per la gestione della grafica e degli sprite.

| Funzione | Parametri | Descrizione |
| --- | --- | --- |
| `gfx_turn_on()` | `()` | Attiva la modalità grafica bitmap. |
| `gfx_turn_off()` | `()` | Disattiva la modalità grafica e torna alla modalità testo. |
| `gfx_clear_screen()` | `()` | Pulisce l'intero schermo grafico. |
| `set_color(color)` | `(color)` | Imposta il colore di sfondo e del bordo. |
| `plot_color(color)` | `(color)` | Imposta il colore per le operazioni di disegno. |
| `plot(x, y)` | `(x, y)` | Disegna un pixel alle coordinate specificate. |
| `unplot(x, y)` | `(x, y)` | Cancella un pixel alle coordinate specificate. |
| `draw_line(x1, y1, x2, y2)` | `(x1, y1, x2, y2)` | Disegna una linea tra due punti. |
| `clear_line(x1, y1, x2, y2)` | `(x1, y1, x2, y2)` | Cancella una linea tra due punti. |
| `draw_circle(x, y, r)` | `(x, y, r)` | Disegna un cerchio. |
| `draw_ellipse(x, y, rx, ry)` | `(x, y, rx, ry)` | Disegna un'ellisse. |
| `draw_rect(x1, y1, x2, y2)` | `(x1, y1, x2, y2)` | Disegna un rettangolo. |
| `scroll(dir, start, end)` | `(direction, start_line, end_line)` | Esegue lo scroll di una porzione dello schermo. |
| `set_cursor(row, col)` | `(row, col)` | Posiziona il cursore testo. |
| `print_char(char_code)` | `(char_code)` | Stampa un carattere in modalità testo. |
| `set_char_color(color_code)` | `(color_code)` | Imposta il colore del testo. |
| `sprite_enable(mask)` | `(mask)` | Abilita gli sprite specificati da una maschera di bit. |
| `sprite_disable(mask)` | `(mask)` | Disabilita gli sprite specificati da una maschera di bit. |
| `sprite_set_pos(num, x, y)` | `(sprite_num, x, y)` | Imposta la posizione di uno sprite. |
| `sprite_set_color(num, color)` | `(sprite_num, color)` | Imposta il colore di uno sprite. |
| `sprite_set_pointer(num, addr)` | `(sprite_num, address)` | Associa un blocco di dati a uno sprite. |
| `sprite_create_from_data(addr, data)` | `(address, data)` | Crea i dati per uno sprite a un indirizzo di memoria. |
| `sprite_expand_x(mask)` | `(mask)` | Espande gli sprite specificati in orizzontale. |
| `sprite_expand_y(mask)` | `(mask)` | Espande gli sprite specificati in verticale. |
| `sprite_set_priority(mask)` | `(mask)` | Imposta la priorità degli sprite (davanti/dietro alla grafica). |
| `sprite_set_multicolor(mask)` | `(mask)` | Abilita la modalità multicolor per gli sprite. |
| `sprite_set_multicolor_colors(mc1, mc2)` | `(mc1, mc2)` | Imposta i due colori globali per gli sprite multicolor. |
| `sprite_set_x_msb(mask)` | `(mask)` | Imposta il bit più significativo della coordinata X per gli sprite. |
| `sprite_set_x_msb_clear(mask)` | `(mask)` | Azzera il bit più significativo della coordinata X per gli sprite. |
| `sprite_check_collision_data()` | `()` | Ritorna una maschera di bit delle collisioni sprite-dati. |
| `sprite_check_collision_sprite()` | `()` | Ritorna una maschera di bit delle collisioni sprite-sprite. |

### Utilizzo delle Routine KERNAL

Alcune delle funzioni di basso livello, come la stampa di un carattere (`print_char`) o il posizionamento del cursore (`set_cursor`), non sono implementate direttamente nel nostro codice assembly, ma utilizzano le **routine KERNAL** del Commodore 64.

Il KERNAL è il "sistema operativo" del C64, un insieme di routine pre-programmate presenti nella ROM del computer che gestiscono operazioni di base come l'input/output e la gestione dello schermo.

Il nostro compilatore genera chiamate a queste routine (ad esempio, `JSR $FFD2` per `CHROUT`) assumendo che il codice verrà eseguito su un C64 dove queste routine sono sempre disponibili a indirizzi di memoria fissi. Questo ci permette di sfruttare le funzionalità del sistema senza doverle riscrivere da zero.

### Routine Manager

#### RoutineManager
- Gestione automatica delle dipendenze tra routine
- Inclusione solo delle routine utilizzate
- Libreria completa di routine matematiche e hardware

### Ottimizzatore

#### PeepholeOptimizer
Ottimizzazioni a livello di assembly:
- Rimozione di jump ridondanti
- Eliminazione di load/store morti
- Combinazione di operazioni consecutive
- Ottimizzazione delle operazioni stack

## 🚀 Installazione e Uso

### Requisiti
```bash
pip install -r requirements.txt
```

### Uso Base

Il compilatore si usa da linea di comando.

**Sintassi:**
```bash
python main.py <file_input.py> -o <file_output.asm>
```

**Esempio:**
1.  Salva il tuo codice Python in un file, per esempio `esempio.py`.
    ```python
    # esempio.py
    def main():
        x = 10
        y = 20
        result = (x + y) * 2
        print(result)

    main()
    ```

2.  Esegui il compilatore:
    ```bash
    python main.py esempio.py -o esempio.asm
    ```

3.  Verrà generato un file `esempio.asm` con il codice assembly 6502 corrispondente.

## 📝 Esempi di Codice

### Esempio 1: Operazioni Aritmetiche
```python
# Python
x = 10
y = 20
result = (x + y) * 2
print(result)
```

### Esempio 2: Controllo di Flusso
```python
# Python
def check_number(n):
    if n > 0:
        return 1
    elif n < 0:
        return -1
    else:
        return 0

result = check_number(5)
print(result)
```

### Esempio 3: Loop
```python
# Python
total = 0
for i in range(10):
    total = total + i
print(total)
```

### Esempio 4: Grafica C64
```python
# Python
gfx_turn_on()
gfx_clear_screen()

# Disegna una linea diagonale
draw_line(0, 0, 319, 199)

# Attiva sprite
sprite_enable(0b00000001)
sprite_set_pos(0, 160, 100)
```

## 🔧 Struttura del Progetto

Il progetto è organizzato in un package `lib` che contiene la logica del compilatore, un file `main.py` come entry point, e una `test_suites` per i test. La libreria `lib` è stata modularizzata per separare le diverse funzionalità.

```
/
├── main.py                 # Entry point della linea di comando
├── README.md
├── lib/                    # Package principale del compilatore
│   ├── __init__.py
│   ├── core.py             # Classe principale Py2C64Compiler
│   ├── abc.py              # Classi base astratte
│   ├── ast_nodes.py        # Nodi dell'AST interno
│   ├── builtins.py         # Definizioni delle funzioni built-in
│   ├── c64.py              # Code generator per C64
│   ├── errors.py           # Eccezioni custom
│   ├── labels.py           # Label manager
│   ├── optimizer.py        # Peephole optimizer
│   ├── output.py           # Gestione output assembly
│   ├── parser.py           # Parser da AST Python a AST interno
│   ├── routines.py         # Gestore delle routine (carica da sub-packages)
│   ├── symbols.py          # Gestore della symbol table e tipi
│   │
│   ├── graphics/           # Package per le routine grafiche
│   │   ├── __init__.py
│   │   ├── drawing.py      # Primitive di disegno (linee, punti)
│   │   ├── scrolling.py    # Routine per lo scrolling
│   │   ├── sprites.py      # Gestione degli sprite
│   │   └── text.py         # Gestione testo in modalità grafica
│   │
│   └── math/               # Package per le routine matematiche
│       ├── __init__.py
│       └── arithmetic.py   # Routine per operazioni matematiche
│
├── test_suites/            # Suite di test di integrazione
│   ├── examples/           # Codici Python di test
│   └── expected_outputs/   # Output assembly attesi
│
└── doc/                    # Documentazione
```

## 🧪 Testing

Il progetto include un framework di test completo:

```python
# Esegui i test
runner = TestRunner()
runner.run_tests()
```

### Test Cases Inclusi
- **Simple Assignment**: Assegnazioni base
- **Arithmetic Operations**: Operazioni aritmetiche
- **Control Flow**: if/else, while, for
- **Functions**: Definizione e chiamata
- **Hardware Features**: Grafica e sprite C64

## 📊 Ottimizzazioni

### Peephole Optimization
- Rimozione di jump ridondanti
- Eliminazione di load/store inutili
- Combinazione di operazioni consecutive
- Ottimizzazione delle operazioni stack

### Memory Management
- Gestione automatica delle variabili temporanee
- Ottimizzazione dell'uso della memoria
- Allocazione efficiente delle variabili

## 🎯 Roadmap

### Versione 1.0 (Corrente)
- ✅ Architettura OOP completa
- ✅ Supporto costrutti Python base
- ✅ Generazione codice 6502
- ✅ Routine hardware C64
- ✅ Ottimizzazioni peephole

### Versione 1.1 (Prossima)
- ⏳ Supporto per array e liste
- ⏳ Gestione delle stringhe migliorata
- ⏳ Routine di I/O avanzate
- ⏳ Supporto per interrupts

### Versione 1.2 (Futura)
- ⏳ Supporto per classi Python
- ⏳ Gestione degli errori runtime
- ⏳ Debugger integrato
- ⏳ IDE con syntax highlighting

## 🐛 Gestione degli Errori

### CompilerError
Classe personalizzata per errori di compilazione:
```python
class CompilerError(Exception):
    def __init__(self, message: str, line: Optional[int] = None, 
                 column: Optional[int] = None):
        # Gestione errori con informazioni di posizione
```

### Tipi di Errore
- **Syntax Errors**: Errori di sintassi Python
- **Type Errors**: Errori di tipo non supportati
- **Scope Errors**: Variabili non definite
- **Function Errors**: Funzioni non trovate
- **Hardware Errors**: Operazioni hardware non supportate

## 📈 Performance

### Ottimizzazioni Implementate
- **Constant Folding**: Valutazione costanti a compile-time
- **Dead Code Elimination**: Rimozione codice morto
- **Register Allocation**: Uso efficiente dei registri 6502
- **Instruction Scheduling**: Riordino istruzioni per performance

### Benchmark
- **Fibonacci(10)**: ~200 bytes di codice generato
- **Bubble Sort**: ~150 bytes per 10 elementi
- **Graphics Demo**: ~500 bytes con routine hardware

## 🤝 Contribuire

### Come Contribuire
1. Fork del repository
2. Crea un branch feature (`git checkout -b feature/amazing-feature`)
3. Commit delle modifiche (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Apri una Pull Request

### Coding Standards
- Segui i principi OOP
- Documenta tutte le funzioni pubbliche
- Includi test per le nuove funzionalità
- Usa type hints quando possibile

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per dettagli.

## 🙏 Ringraziamenti

- Commodore 64 community per documentazione hardware
- Python AST documentation
- 6502 assembly reference guides
- Retro computing enthusiasts

## 📞 Contatti

- **GitHub**: [repository-link]
- **Email**: [your-email]
- **Forum**: [retro-computing-forum]

---

*py2c64 - Bringing Python to the Commodore 64, one instruction at a time!* 🚀