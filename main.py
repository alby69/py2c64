"""
py2c64 - Riprogettazione Object-Oriented
Un compiler Python-to-6502 per Commodore 64 riprogettato con principi OOP
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set
from enum import Enum
import ast
from dataclasses import dataclass, field

# ============================================================================
# CORE TYPES E ENUMS
# ============================================================================

class DataType(Enum):
    INT16 = "int16"
    FLOAT32 = "float32"
    STRING = "string"
    VOID = "void"

class OperationType(Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    EQ = "eq"
    NE = "ne"
    LT = "lt"
    GT = "gt"
    LE = "le"
    GE = "ge"

@dataclass
class Variable:
    name: str
    data_type: DataType
    address: Optional[int] = None
    scope: str = "global"
    is_parameter: bool = False

@dataclass
class Function:
    name: str
    parameters: List[Variable]
    return_type: DataType
    local_vars: Dict[str, Variable] = field(default_factory=dict)
    entry_label: Optional[str] = None

# ============================================================================
# SYMBOL TABLE MANAGEMENT
# ============================================================================

class SymbolTable:
    """Gestisce simboli, variabili e scope in modo strutturato"""
    
    def __init__(self):
        self.global_vars: Dict[str, Variable] = {}
        self.functions: Dict[str, Function] = {}
        self.current_scope: str = "global"
        self.scope_stack: List[str] = ["global"]
        self.local_vars_stack: List[Dict[str, Variable]] = [{}]
    
    def enter_scope(self, scope_name: str):
        """Entra in un nuovo scope (funzione)"""
        self.scope_stack.append(scope_name)
        self.current_scope = scope_name
        self.local_vars_stack.append({})
    
    def exit_scope(self):
        """Esce dallo scope corrente"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.local_vars_stack.pop()
            self.current_scope = self.scope_stack[-1]
    
    def declare_variable(self, name: str, data_type: DataType) -> Variable:
        """Dichiara una nuova variabile nello scope corrente"""
        var = Variable(name, data_type, scope=self.current_scope)
        
        if self.current_scope == "global":
            self.global_vars[name] = var
        else:
            self.local_vars_stack[-1][name] = var
        
        return var
    
    def lookup_variable(self, name: str) -> Optional[Variable]:
        """Cerca una variabile negli scope disponibili"""
        # Prima cerca negli scope locali (dal più profondo al più superficiale)
        for local_vars in reversed(self.local_vars_stack[1:]):
            if name in local_vars:
                return local_vars[name]
        
        # Poi cerca nelle variabili globali
        return self.global_vars.get(name)
    
    def declare_function(self, name: str, params: List[Variable], return_type: DataType) -> Function:
        """Dichiara una nuova funzione"""
        func = Function(name, params, return_type)
        self.functions[name] = func
        return func
    
    def lookup_function(self, name: str) -> Optional[Function]:
        """Cerca una funzione"""
        return self.functions.get(name)

# ============================================================================
# LABEL MANAGEMENT
# ============================================================================

class LabelManager:
    """Gestisce la generazione di label univoche per assembly"""
    
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.used_labels: Set[str] = set()
    
    def generate_label(self, prefix: str = "L") -> str:
        """Genera una label univoca con il prefisso specificato"""
        if prefix not in self.counters:
            self.counters[prefix] = 0
        
        while True:
            label = f"{prefix}{self.counters[prefix]}"
            self.counters[prefix] += 1
            
            if label not in self.used_labels:
                self.used_labels.add(label)
                return label

# ============================================================================
# ASSEMBLY OUTPUT MANAGEMENT
# ============================================================================

class AssemblyOutput:
    """Gestisce l'output assembly con sezioni organizzate"""
    
    def __init__(self):
        self.data_section: List[str] = []
        self.code_section: List[str] = []
        self.routines_section: List[str] = []
        self.current_section: List[str] = self.code_section
    
    def add_line(self, line: str):
        """Aggiunge una riga alla sezione corrente"""
        self.current_section.append(line)
    
    def add_lines(self, lines: List[str]):
        """Aggiunge multiple righe alla sezione corrente"""
        self.current_section.extend(lines)
    
    def add_label(self, label: str):
        """Aggiunge una label"""
        self.add_line(f"{label}:")
    
    def add_instruction(self, opcode: str, operand: str = ""):
        """Aggiunge un'istruzione assembly"""
        if operand:
            self.add_line(f"    {opcode} {operand}")
        else:
            self.add_line(f"    {opcode}")
    
    def switch_to_data_section(self):
        """Cambia alla sezione dati"""
        self.current_section = self.data_section
    
    def switch_to_code_section(self):
        """Cambia alla sezione codice"""
        self.current_section = self.code_section
    
    def switch_to_routines_section(self):
        """Cambia alla sezione routine"""
        self.current_section = self.routines_section
    
    def generate(self) -> str:
        """Genera l'output assembly completo"""
        result = []
        
        if self.data_section:
            result.append("; === DATA SECTION ===")
            result.extend(self.data_section)
            result.append("")
        
        if self.code_section:
            result.append("; === CODE SECTION ===")
            result.extend(self.code_section)
            result.append("")
        
        if self.routines_section:
            result.append("; === ROUTINES SECTION ===")
            result.extend(self.routines_section)
            result.append("")
        
        return "\n".join(result)

# ============================================================================
# ABSTRACT SYNTAX TREE NODES
# ============================================================================

class ASTNode(ABC):
    """Classe base per tutti i nodi dell'AST"""
    
    @abstractmethod
    def accept(self, visitor: 'CodeGenerator') -> Any:
        pass

class Expression(ASTNode):
    """Classe base per tutte le espressioni"""
    pass

class Statement(ASTNode):
    """Classe base per tutti i statement"""
    pass

class Literal(Expression):
    """Nodo per valori letterali"""
    
    def __init__(self, value: Any, data_type: DataType):
        self.value = value
        self.data_type = data_type
    
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_literal(self)

class Identifier(Expression):
    """Nodo per identificatori (variabili)"""
    
    def __init__(self, name: str):
        self.name = name
    
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_identifier(self)

class BinaryOperation(Expression):
    """Nodo per operazioni binarie"""
    
    def __init__(self, left: Expression, operation: OperationType, right: Expression):
        self.left = left
        self.operation = operation
        self.right = right
    
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_binary_operation(self)

class FunctionCall(Expression):
    """Nodo per chiamate di funzione"""
    
    def __init__(self, name: str, arguments: List[Expression]):
        self.name = name
        self.arguments = arguments
    
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_function_call(self)

class Assignment(Statement):
    """Nodo per assegnazioni"""
    
    def __init__(self, target: str, value: Expression):
        self.target = target
        self.value = value
    
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_assignment(self)

class IfStatement(Statement):
    """Nodo per statement if"""
    
    def __init__(self, condition: Expression, then_body: List[Statement], else_body: Optional[List[Statement]] = None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body or []
    
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_if_statement(self)

class WhileStatement(Statement):
    """Nodo per loop while"""
    
    def __init__(self, condition: Expression, body: List[Statement]):
        self.condition = condition
        self.body = body
    
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_while_statement(self)

class ForStatement(Statement):
    """Nodo per loop for"""
    
    def __init__(self, var: str, start: Expression, end: Expression, step: Expression, body: List[Statement]):
        self.var = var
        self.start = start
        self.end = end
        self.step = step
        self.body = body
    
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_for_statement(self)

class FunctionDefinition(Statement):
    """Nodo per definizioni di funzione"""
    
    def __init__(self, name: str, parameters: List[Variable], body: List[Statement], return_type: DataType):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.return_type = return_type
    
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_function_definition(self)

class ReturnStatement(Statement):
    """Nodo per statement return"""
    
    def __init__(self, value: Optional[Expression] = None):
        self.value = value
    
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_return_statement(self)

class Program(ASTNode):
    """Nodo radice del programma"""
    
    def __init__(self, statements: List[Statement]):
        self.statements = statements
    
    def accept(self, visitor: 'CodeGenerator') -> Any:
        return visitor.visit_program(self)

# ============================================================================
# CODE GENERATORS (VISITOR PATTERN)
# ============================================================================

class CodeGenerator(ABC):
    """Visitor astratto per la generazione del codice"""
    
    def __init__(self, symbol_table: SymbolTable, label_manager: LabelManager, output: AssemblyOutput):
        self.symbol_table = symbol_table
        self.label_manager = label_manager
        self.output = output
    
    @abstractmethod
    def visit_program(self, node: Program) -> Any:
        pass
    
    @abstractmethod
    def visit_literal(self, node: Literal) -> Any:
        pass
    
    @abstractmethod
    def visit_identifier(self, node: Identifier) -> Any:
        pass
    
    @abstractmethod
    def visit_binary_operation(self, node: BinaryOperation) -> Any:
        pass
    
    @abstractmethod
    def visit_function_call(self, node: FunctionCall) -> Any:
        pass
    
    @abstractmethod
    def visit_assignment(self, node: Assignment) -> Any:
        pass
    
    @abstractmethod
    def visit_if_statement(self, node: IfStatement) -> Any:
        pass
    
    @abstractmethod
    def visit_while_statement(self, node: WhileStatement) -> Any:
        pass
    
    @abstractmethod
    def visit_for_statement(self, node: ForStatement) -> Any:
        pass
    
    @abstractmethod
    def visit_function_definition(self, node: FunctionDefinition) -> Any:
        pass
    
    @abstractmethod
    def visit_return_statement(self, node: ReturnStatement) -> Any:
        pass

# ============================================================================
# 6502 CODE GENERATOR
# ============================================================================

class C64CodeGenerator(CodeGenerator):
    """Generatore di codice 6502 per Commodore 64"""
    
    def __init__(self, symbol_table: SymbolTable, label_manager: LabelManager, output: AssemblyOutput):
        super().__init__(symbol_table, label_manager, output)
        self.temp_var_counter = 0
        self.used_routines: Set[str] = set()
    
    def visit_program(self, node: Program) -> Any:
        """Visita il programma principale"""
        self.output.add_line("; py2c64 - Generated 6502 Assembly")
        self.output.add_line("; Target: Commodore 64")
        self.output.add_line("")
        
        # Processa tutti i statement
        for stmt in node.statements:
            stmt.accept(self)
        
        # Aggiunge le routine utilizzate
        self._add_used_routines()
        
        return self.output.generate()
    
    def visit_literal(self, node: Literal) -> Any:
        """Visita un valore letterale"""
        temp_var = self._get_temp_var()
        
        if node.data_type == DataType.INT16:
            self.output.add_instruction("LDA", f"#<{node.value}")
            self.output.add_instruction("STA", f"{temp_var}")
            self.output.add_instruction("LDA", f"#{node.value}>>8")
            self.output.add_instruction("STA", f"{temp_var}+1")
        elif node.data_type == DataType.FLOAT32:
            # Per i float sarebbe necessario convertire in formato Apple II
            self.output.add_line(f"    ; Float literal: {node.value}")
        
        return temp_var
    
    def visit_identifier(self, node: Identifier) -> Any:
        """Visita un identificatore"""
        var = self.symbol_table.lookup_variable(node.name)
        if not var:
            raise CompilerError(f"Undefined variable: {node.name}")
        
        temp_var = self._get_temp_var()
        self.output.add_instruction("LDA", f"{var.name}")
        self.output.add_instruction("STA", f"{temp_var}")
        self.output.add_instruction("LDA", f"{var.name}+1")
        self.output.add_instruction("STA", f"{temp_var}+1")
        
        return temp_var
    
    def visit_binary_operation(self, node: BinaryOperation) -> Any:
        """Visita un'operazione binaria"""
        left_result = node.left.accept(self)
        right_result = node.right.accept(self)
        result_var = self._get_temp_var()
        
        if node.operation == OperationType.ADD:
            self._generate_add_int16(left_result, right_result, result_var)
        elif node.operation == OperationType.SUB:
            self._generate_sub_int16(left_result, right_result, result_var)
        elif node.operation == OperationType.MUL:
            self._generate_mul_int16(left_result, right_result, result_var)
            self.used_routines.add("multiply16x16")
        # ... altri operatori
        
        return result_var
    
    def visit_function_call(self, node: FunctionCall) -> Any:
        """Visita una chiamata di funzione"""
        if node.name == "print":
            # Gestione speciale per print
            if node.arguments:
                arg_result = node.arguments[0].accept(self)
                self.output.add_instruction("LDA", f"{arg_result}")
                self.output.add_instruction("STA", "PRINT_VALUE")
                self.output.add_instruction("LDA", f"{arg_result}+1")
                self.output.add_instruction("STA", "PRINT_VALUE+1")
                self.output.add_instruction("JSR", "PRINT_INT16")
                self.used_routines.add("print_int16")
        else:
            # Chiamata di funzione normale
            func = self.symbol_table.lookup_function(node.name)
            if not func:
                raise CompilerError(f"Undefined function: {node.name}")
            
            # Gestione parametri e chiamata
            for i, arg in enumerate(node.arguments):
                arg_result = arg.accept(self)
                self.output.add_instruction("LDA", f"{arg_result}")
                self.output.add_instruction("PHA")
                self.output.add_instruction("LDA", f"{arg_result}+1")
                self.output.add_instruction("PHA")
            
            self.output.add_instruction("JSR", f"FUNC_{node.name}")
    
    def visit_assignment(self, node: Assignment) -> Any:
        """Visita un'assegnazione"""
        value_result = node.value.accept(self)
        
        # Cerca o crea la variabile
        var = self.symbol_table.lookup_variable(node.target)
        if not var:
            # Inferisci il tipo dall'espressione (semplificato)
            var = self.symbol_table.declare_variable(node.target, DataType.INT16)
        
        self.output.add_instruction("LDA", f"{value_result}")
        self.output.add_instruction("STA", f"{var.name}")
        self.output.add_instruction("LDA", f"{value_result}+1")
        self.output.add_instruction("STA", f"{var.name}+1")
    
    def visit_if_statement(self, node: IfStatement) -> Any:
        """Visita uno statement if"""
        condition_result = node.condition.accept(self)
        else_label = self.label_manager.generate_label("ELSE")
        end_label = self.label_manager.generate_label("END_IF")
        
        # Test condizione (semplificato: != 0)
        self.output.add_instruction("LDA", f"{condition_result}")
        self.output.add_instruction("ORA", f"{condition_result}+1")
        self.output.add_instruction("BEQ", else_label)
        
        # Then body
        for stmt in node.then_body:
            stmt.accept(self)
        
        self.output.add_instruction("JMP", end_label)
        
        # Else body
        self.output.add_label(else_label)
        for stmt in node.else_body:
            stmt.accept(self)
        
        self.output.add_label(end_label)
    
    def visit_while_statement(self, node: WhileStatement) -> Any:
        """Visita un loop while"""
        loop_label = self.label_manager.generate_label("WHILE_LOOP")
        end_label = self.label_manager.generate_label("END_WHILE")
        
        self.output.add_label(loop_label)
        
        # Test condizione
        condition_result = node.condition.accept(self)
        self.output.add_instruction("LDA", f"{condition_result}")
        self.output.add_instruction("ORA", f"{condition_result}+1")
        self.output.add_instruction("BEQ", end_label)
        
        # Body
        for stmt in node.body:
            stmt.accept(self)
        
        self.output.add_instruction("JMP", loop_label)
        self.output.add_label(end_label)
    
    def visit_for_statement(self, node: ForStatement) -> Any:
        """Visita un loop for"""
        # Implementazione semplificata per for i in range(start, end, step)
        loop_label = self.label_manager.generate_label("FOR_LOOP")
        end_label = self.label_manager.generate_label("END_FOR")
        
        # Inizializzazione
        start_result = node.start.accept(self)
        var = self.symbol_table.declare_variable(node.var, DataType.INT16)
        
        self.output.add_instruction("LDA", f"{start_result}")
        self.output.add_instruction("STA", f"{var.name}")
        self.output.add_instruction("LDA", f"{start_result}+1")
        self.output.add_instruction("STA", f"{var.name}+1")
        
        # Loop
        self.output.add_label(loop_label)
        
        # Test condizione (var < end)
        end_result = node.end.accept(self)
        self._generate_compare_int16(var.name, end_result, "LT")
        self.output.add_instruction("BEQ", end_label)
        
        # Body
        for stmt in node.body:
            stmt.accept(self)
        
        # Incremento
        step_result = node.step.accept(self)
        self._generate_add_int16(var.name, step_result, var.name)
        self.output.add_instruction("JMP", loop_label)
        self.output.add_label(end_label)
    
    def visit_function_definition(self, node: FunctionDefinition) -> Any:
        """Visita una definizione di funzione"""
        func = self.symbol_table.declare_function(node.name, node.parameters, node.return_type)
        func.entry_label = f"FUNC_{node.name}"
        
        self.symbol_table.enter_scope(node.name)
        
        # Dichiarazione parametri
        for param in node.parameters:
            self.symbol_table.declare_variable(param.name, param.data_type)
        
        # Generazione codice
        self.output.add_label(func.entry_label)
        
        # Prologue
        self.output.add_instruction("TSX")
        self.output.add_instruction("STX", "FRAME_POINTER")
        
        # Body
        for stmt in node.body:
            stmt.accept(self)
        
        # Epilogue (se non c'è return esplicito)
        self.output.add_instruction("RTS")
        
        self.symbol_table.exit_scope()
    
    def visit_return_statement(self, node: ReturnStatement) -> Any:
        """Visita uno statement return"""
        if node.value:
            result = node.value.accept(self)
            self.output.add_instruction("LDA", f"{result}")
            self.output.add_instruction("STA", "RETURN_VALUE")
            self.output.add_instruction("LDA", f"{result}+1")
            self.output.add_instruction("STA", "RETURN_VALUE+1")
        
        self.output.add_instruction("RTS")
    
    # Metodi helper
    def _get_temp_var(self) -> str:
        """Genera una variabile temporanea"""
        temp_name = f"TEMP_{self.temp_var_counter}"
        self.temp_var_counter += 1
        return temp_name
    
    def _generate_add_int16(self, left: str, right: str, result: str):
        """Genera codice per addizione a 16 bit"""
        self.output.add_instruction("CLC")
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("ADC", f"{right}")
        self.output.add_instruction("STA", f"{result}")
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("ADC", f"{right}+1")
        self.output.add_instruction("STA", f"{result}+1")
    
    def _generate_sub_int16(self, left: str, right: str, result: str):
        """Genera codice per sottrazione a 16 bit"""
        self.output.add_instruction("SEC")
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("SBC", f"{right}")
        self.output.add_instruction("STA", f"{result}")
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("SBC", f"{right}+1")
        self.output.add_instruction("STA", f"{result}+1")
    
    def _generate_mul_int16(self, left: str, right: str, result: str):
        """Genera codice per moltiplicazione a 16 bit"""
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("STA", "MULT_ARG1")
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("STA", "MULT_ARG1+1")
        self.output.add_instruction("LDA", f"{right}")
        self.output.add_instruction("STA", "MULT_ARG2")
        self.output.add_instruction("LDA", f"{right}+1")
        self.output.add_instruction("STA", "MULT_ARG2+1")
        self.output.add_instruction("JSR", "MULTIPLY16x16")
        self.output.add_instruction("LDA", "MULT_RESULT")
        self.output.add_instruction("STA", f"{result}")
        self.output.add_instruction("LDA", "MULT_RESULT+1")
        self.output.add_instruction("STA", f"{result}+1")
    
    def _generate_compare_int16(self, left: str, right: str, op: str):
        """Genera codice per confronto a 16 bit"""
        # Implementazione semplificata
        self.output.add_instruction("LDA", f"{left}")
        self.output.add_instruction("CMP", f"{right}")
        self.output.add_instruction("LDA", f"{left}+1")
        self.output.add_instruction("SBC", f"{right}+1")
    
    def _add_used_routines(self):
        """Aggiunge le routine utilizzate alla sezione routine"""
        self.output.switch_to_routines_section()
        
        if "multiply16x16" in self.used_routines:
            self.output.add_lines([
                "MULTIPLY16x16:",
                "    ; Routine di moltiplicazione 16x16",
                "    ; Input: MULT_ARG1, MULT_ARG2",
                "    ; Output: MULT_RESULT",
                "    ; ... codice assembly ...",
                "    RTS"
            ])
        
        if "print_int16" in self.used_routines:
            self.output.add_lines([
                "PRINT_INT16:",
                "    ; Routine per stampare intero 16 bit",
                "    ; Input: PRINT_VALUE",
                "    ; ... codice assembly ...",
                "    RTS"
            ])

# ============================================================================
# PARSER (Python AST -> Internal AST)
# ============================================================================

class PythonASTParser:
    """Parser che converte l'AST Python nel nostro AST interno"""
    
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
    
    def parse(self, python_code: str) -> Program:
        """Parsa codice Python e ritorna il nostro AST"""
        python_ast = ast.parse(python_code)
        statements = []
        
        for node in python_ast.body:
            stmt = self._parse_statement(node)
            if stmt:
                statements.append(stmt)
        
        return Program(statements)
    
    def _parse_statement(self, node: ast.AST) -> Optional[Statement]:
        """Parsa un statement Python"""
        if isinstance(node, ast.Assign):
            return self._parse_assignment(node)
        elif isinstance(node, ast.If):
            return self._parse_if_statement(node)
        elif isinstance(node, ast.While):
            return self._parse_while_statement(node)
        elif isinstance(node, ast.For):
            return self._parse_for_statement(node)
        elif isinstance(node, ast.FunctionDef):
            return self._parse_function_definition(node)
        elif isinstance(node, ast.Return):
            return self._parse_return_statement(node)
        elif isinstance(node, ast.Expr):
            # Statement di espressione (es. chiamata di funzione)
            return self._parse_expression_statement(node)
        
        return None
    
    def _parse_assignment(self, node: ast.Assign) -> Assignment:
        """Parsa un'assegnazione"""
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            raise CompilerError("Only simple assignments are supported")
        
        target = node.targets[0].id
        value = self._parse_expression(node.value)
        return Assignment(target, value)
    
    def _parse_if_statement(self, node: ast.If) -> IfStatement:
        """Parsa uno statement if"""
        condition = self._parse_expression(node.test)
        then_body = [self._parse_statement(stmt) for stmt in node.body]
        then_body = [stmt for stmt in then_body if stmt is not None]
        
        else_body = []
        if node.orelse:
            else_body = [self._parse_statement(stmt) for stmt in node.orelse]
            else_body = [stmt for stmt in else_body if stmt is not None]
        
        return IfStatement(condition, then_body, else_body)
    
    def _parse_while_statement(self, node: ast.While) -> WhileStatement:
        """Parsa un loop while"""
        condition = self._parse_expression(node.test)
        body = [self._parse_statement(stmt) for stmt in node.body]
        body = [stmt for stmt in body if stmt is not None]
        return WhileStatement(condition, body)
    
    def _parse_for_statement(self, node: ast.For) -> ForStatement:
        """Parsa un loop for (supporta solo range)"""
        if not isinstance(node.target, ast.Name):
            raise CompilerError("Only simple for loop variables are supported")
        
        var_name = node.target.id
        
        # Supporta solo for i in range(...)
        if not isinstance(node.iter, ast.Call) or not isinstance(node.iter.func, ast.Name) or node.iter.func.id != "range":
            raise CompilerError("Only range() iterations are supported")
        
        range_args = node.iter.args
        if len(range_args) == 1:
            # range(stop)
            start = Literal(0, DataType.INT16)
            end = self._parse_expression(range_args[0])
            step = Literal(1, DataType.INT16)
        elif len(range_args) == 2:
            # range(start, stop)
            start = self._parse_expression(range_args[0])
            end = self._parse_expression(range_args[1])
            step = Literal(1, DataType.INT16)
        elif len(range_args) == 3:
            # range(start, stop, step)
            start = self._parse_expression(range_args[0])
            end = self._parse_expression(range_args[1])
            step = self._parse_expression(range_args[2])
        else:
            raise CompilerError("Invalid range() arguments")
        
        body = [self._parse_statement(stmt) for stmt in node.body]
        body = [stmt for stmt in body if stmt is not None]
        
        return ForStatement(var_name, start, end, step, body)
    
    def _parse_function_definition(self, node: ast.FunctionDef) -> FunctionDefinition:
        """Parsa una definizione di funzione"""
        name = node.name
        
        # Parsa parametri
        parameters = []
        for arg in node.args.args:
            # Tipo inferito come INT16 per default
            param = Variable(arg.arg, DataType.INT16, is_parameter=True)
            parameters.append(param)
        
        # Parsa corpo
        body = [self._parse_statement(stmt) for stmt in node.body]
        body = [stmt for stmt in body if stmt is not None]
        
        # Tipo di ritorno inferito (semplificato)
        return_type = DataType.VOID
        for stmt in body:
            if isinstance(stmt, ReturnStatement) and stmt.value:
                return_type = DataType.INT16
                break
        
        return FunctionDefinition(name, parameters, body, return_type)
    
    def _parse_return_statement(self, node: ast.Return) -> ReturnStatement:
        """Parsa uno statement return"""
        value = None
        if node.value:
            value = self._parse_expression(node.value)
        return ReturnStatement(value)
    
    def _parse_expression_statement(self, node: ast.Expr) -> Optional[Statement]:
        """Parsa un'espressione usata come statement"""
        # Per ora convertiamo solo le chiamate di funzione
        if isinstance(node.value, ast.Call):
            # Crea un assignment temporaneo per gestire la chiamata
            call_expr = self._parse_expression(node.value)
            return Assignment("_temp_call", call_expr)
        return None
    
    def _parse_expression(self, node: ast.AST) -> Expression:
        """Parsa un'espressione"""
        if isinstance(node, ast.Constant):
            return self._parse_constant(node)
        elif isinstance(node, ast.Name):
            return Identifier(node.id)
        elif isinstance(node, ast.BinOp):
            return self._parse_binary_operation(node)
        elif isinstance(node, ast.Call):
            return self._parse_function_call(node)
        elif isinstance(node, ast.Compare):
            return self._parse_comparison(node)
        else:
            raise CompilerError(f"Unsupported expression type: {type(node)}")
    
    def _parse_constant(self, node: ast.Constant) -> Literal:
        """Parsa una costante"""
        value = node.value
        if isinstance(value, int):
            return Literal(value, DataType.INT16)
        elif isinstance(value, float):
            return Literal(value, DataType.FLOAT32)
        elif isinstance(value, str):
            return Literal(value, DataType.STRING)
        else:
            raise CompilerError(f"Unsupported constant type: {type(value)}")
    
    def _parse_binary_operation(self, node: ast.BinOp) -> BinaryOperation:
        """Parsa un'operazione binaria"""
        left = self._parse_expression(node.left)
        right = self._parse_expression(node.right)
        
        op_map = {
            ast.Add: OperationType.ADD,
            ast.Sub: OperationType.SUB,
            ast.Mult: OperationType.MUL,
            ast.FloorDiv: OperationType.DIV,
            ast.Mod: OperationType.MOD,
            ast.BitXor: OperationType.ADD,  # Mapping temporaneo per ^
        }
        
        op_type = op_map.get(type(node.op))
        if not op_type:
            raise CompilerError(f"Unsupported binary operation: {type(node.op)}")
        
        return BinaryOperation(left, op_type, right)
    
    def _parse_function_call(self, node: ast.Call) -> FunctionCall:
        """Parsa una chiamata di funzione"""
        if not isinstance(node.func, ast.Name):
            raise CompilerError("Only simple function calls are supported")
        
        name = node.func.id
        arguments = [self._parse_expression(arg) for arg in node.args]
        
        return FunctionCall(name, arguments)
    
    def _parse_comparison(self, node: ast.Compare) -> BinaryOperation:
        """Parsa un confronto (semplificato per un solo operatore)"""
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise CompilerError("Only simple comparisons are supported")
        
        left = self._parse_expression(node.left)
        right = self._parse_expression(node.comparators[0])
        
        op_map = {
            ast.Eq: OperationType.EQ,
            ast.NotEq: OperationType.NE,
            ast.Lt: OperationType.LT,
            ast.Gt: OperationType.GT,
            ast.LtE: OperationType.LE,
            ast.GtE: OperationType.GE,
        }
        
        op_type = op_map.get(type(node.ops[0]))
        if not op_type:
            raise CompilerError(f"Unsupported comparison: {type(node.ops[0])}")
        
        return BinaryOperation(left, op_type, right)

# ============================================================================
# HARDWARE LIBRARIES
# ============================================================================

class C64HardwareLibrary:
    """Libreria per le funzioni hardware del C64"""
    
    @staticmethod
    def get_graphics_routines() -> Dict[str, List[str]]:
        """Ritorna le routine per la grafica"""
        return {
            "gfx_turn_on": [
                "GFX_TURN_ON:",
                "    LDA #$3B",
                "    STA $D011",
                "    LDA #$18",
                "    STA $D018",
                "    RTS"
            ],
            "gfx_turn_off": [
                "GFX_TURN_OFF:",
                "    LDA #$1B",
                "    STA $D011",
                "    RTS"
            ],
            "gfx_clear_screen": [
                "GFX_CLEAR_SCREEN:",
                "    LDA #$00",
                "    LDX #$00",
                "GFX_CLEAR_LOOP:",
                "    STA $2000,X",
                "    STA $2100,X",
                "    STA $2200,X",
                "    STA $2300,X",
                "    STA $2400,X",
                "    STA $2500,X",
                "    STA $2600,X",
                "    STA $2700,X",
                "    STA $2800,X",
                "    STA $2900,X",
                "    STA $2A00,X",
                "    STA $2B00,X",
                "    STA $2C00,X",
                "    STA $2D00,X",
                "    STA $2E00,X",
                "    STA $2F00,X",
                "    STA $3000,X",
                "    STA $3100,X",
                "    STA $3200,X",
                "    STA $3300,X",
                "    STA $3400,X",
                "    STA $3500,X",
                "    STA $3600,X",
                "    STA $3700,X",
                "    STA $3800,X",
                "    STA $3900,X",
                "    STA $3A00,X",
                "    STA $3B00,X",
                "    STA $3C00,X",
                "    STA $3D00,X",
                "    STA $3E00,X",
                "    STA $3F00,X",
                "    INX",
                "    BNE GFX_CLEAR_LOOP",
                "    RTS"
            ],
            "draw_line": [
                "DRAW_LINE:",
                "    ; Implementazione algoritmo di Bresenham",
                "    ; Input: X1, Y1, X2, Y2",
                "    ; ... codice assembly completo ...",
                "    RTS"
            ]
        }
    
    @staticmethod
    def get_sprite_routines() -> Dict[str, List[str]]:
        """Ritorna le routine per gli sprite"""
        return {
            "sprite_enable": [
                "SPRITE_ENABLE:",
                "    LDA SPRITE_MASK",
                "    ORA $D015",
                "    STA $D015",
                "    RTS"
            ],
            "sprite_disable": [
                "SPRITE_DISABLE:",
                "    LDA SPRITE_MASK",
                "    EOR #$FF",
                "    AND $D015",
                "    STA $D015",
                "    RTS"
            ],
            "sprite_set_pos": [
                "SPRITE_SET_POS:",
                "    ; Input: SPRITE_NUM, SPRITE_X, SPRITE_Y",
                "    LDA SPRITE_NUM",
                "    ASL",
                "    TAX",
                "    LDA SPRITE_X",
                "    STA $D000,X",
                "    LDA SPRITE_Y",
                "    STA $D001,X",
                "    RTS"
            ]
        }

# ============================================================================
# ROUTINE MANAGER
# ============================================================================

class RoutineManager:
    """Gestisce le routine di libreria e le dipendenze"""
    
    def __init__(self):
        self.available_routines = {}
        self.dependencies = {}
        self.used_routines = set()
        
        # Carica routine hardware
        self.available_routines.update(C64HardwareLibrary.get_graphics_routines())
        self.available_routines.update(C64HardwareLibrary.get_sprite_routines())
        
        # Carica routine matematiche
        self.available_routines.update(self._get_math_routines())
        
        # Definisci dipendenze
        self.dependencies = {
            "draw_line": ["multiply16x16"],
            "draw_ellipse": ["multiply16x16", "sqrt_int16"],
            "print_int16": ["divide16x16"]
        }
    
    def _get_math_routines(self) -> Dict[str, List[str]]:
        """Ritorna le routine matematiche"""
        return {
            "multiply16x16": [
                "MULTIPLY16x16:",
                "    ; Moltiplicazione 16x16 -> 32 bit",
                "    ; Input: MULT_ARG1, MULT_ARG2",
                "    ; Output: MULT_RESULT (32 bit)",
                "    LDA #$00",
                "    STA MULT_RESULT",
                "    STA MULT_RESULT+1",
                "    STA MULT_RESULT+2",
                "    STA MULT_RESULT+3",
                "    LDX #$10",
                "MULT_LOOP:",
                "    LSR MULT_ARG1+1",
                "    ROR MULT_ARG1",
                "    BCC MULT_SKIP",
                "    CLC",
                "    LDA MULT_RESULT",
                "    ADC MULT_ARG2",
                "    STA MULT_RESULT",
                "    LDA MULT_RESULT+1",
                "    ADC MULT_ARG2+1",
                "    STA MULT_RESULT+1",
                "    LDA MULT_RESULT+2",
                "    ADC #$00",
                "    STA MULT_RESULT+2",
                "    LDA MULT_RESULT+3",
                "    ADC #$00",
                "    STA MULT_RESULT+3",
                "MULT_SKIP:",
                "    ASL MULT_ARG2",
                "    ROL MULT_ARG2+1",
                "    DEX",
                "    BNE MULT_LOOP",
                "    RTS"
            ],
            "divide16x16": [
                "DIVIDE16x16:",
                "    ; Divisione 16x16 -> 16 bit",
                "    ; Input: DIV_DIVIDEND, DIV_DIVISOR",
                "    ; Output: DIV_QUOTIENT, DIV_REMAINDER",
                "    ; ... implementazione completa ...",
                "    RTS"
            ],
            "sqrt_int16": [
                "SQRT_INT16:",
                "    ; Radice quadrata approssimata per interi",
                "    ; Input: SQRT_ARG",
                "    ; Output: SQRT_RESULT",
                "    ; ... implementazione completa ...",
                "    RTS"
            ]
        }
    
    def mark_routine_used(self, routine_name: str):
        """Marca una routine come utilizzata"""
        self.used_routines.add(routine_name)
        
        # Aggiungi le dipendenze
        if routine_name in self.dependencies:
            for dep in self.dependencies[routine_name]:
                self.used_routines.add(dep)
    
    def get_used_routines_code(self) -> List[str]:
        """Ritorna il codice assembly di tutte le routine utilizzate"""
        code = []
        
        for routine_name in self.used_routines:
            if routine_name in self.available_routines:
                code.extend(self.available_routines[routine_name])
                code.append("")  # Riga vuota tra routine
        
        return code

# ============================================================================
# OTTIMIZZATORE
# ============================================================================

class PeepholeOptimizer:
    """Ottimizzatore peephole per rimuovere codice ridondante"""
    
    def __init__(self):
        self.optimizations = [
            self._remove_redundant_jumps,
            self._remove_dead_loads,
            self._combine_loads_stores,
            self._optimize_stack_operations
        ]
    
    def optimize(self, assembly_lines: List[str]) -> List[str]:
        """Applica tutte le ottimizzazioni"""
        optimized = assembly_lines[:]
        
        for optimization in self.optimizations:
            optimized = optimization(optimized)
        
        return optimized
    
    def _remove_redundant_jumps(self, lines: List[str]) -> List[str]:
        """Rimuove JMP ridondanti"""
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Cerca pattern: JMP LABEL seguito da LABEL:
            if (line.startswith("JMP ") and 
                i + 1 < len(lines) and 
                lines[i + 1].strip() == line[4:] + ":"):
                # Salta il JMP ridondante
                i += 1
                continue
            
            result.append(lines[i])
            i += 1
        
        return result
    
    def _remove_dead_loads(self, lines: List[str]) -> List[str]:
        """Rimuove LDA/STA ridondanti"""
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Cerca pattern: LDA addr; STA addr (stesso indirizzo)
            if (line.startswith("LDA ") and 
                i + 1 < len(lines) and 
                lines[i + 1].strip() == f"STA {line[4:]}"):
                # Salta entrambe le istruzioni
                i += 2
                continue
            
            result.append(lines[i])
            i += 1
        
        return result
    
    def _combine_loads_stores(self, lines: List[str]) -> List[str]:
        """Combina operazioni di caricamento/salvataggio consecutive"""
        # Implementazione semplificata
        return lines
    
    def _optimize_stack_operations(self, lines: List[str]) -> List[str]:
        """Ottimizza operazioni stack PHA/PLA consecutive"""
        # Implementazione semplificata
        return lines

# ============================================================================
# GESTIONE ERRORI
# ============================================================================

class CompilerError(Exception):
    """Eccezione personalizzata per errori di compilazione"""
    
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Formatta il messaggio di errore con informazioni di posizione"""
        if self.line is not None:
            if self.column is not None:
                return f"Error at line {self.line}, column {self.column}: {self.message}"
            else:
                return f"Error at line {self.line}: {self.message}"
        else:
            return f"Compilation error: {self.message}"

# ============================================================================
# COMPILER PRINCIPALE
# ============================================================================

class Py2C64Compiler:
    """Compiler principale che orchestra tutto il processo"""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.label_manager = LabelManager()
        self.output = AssemblyOutput()
        self.parser = PythonASTParser(self.symbol_table)
        self.code_generator = C64CodeGenerator(self.symbol_table, self.label_manager, self.output)
        self.routine_manager = RoutineManager()
        self.optimizer = PeepholeOptimizer()
    
    def compile(self, python_code: str) -> str:
        """Compila codice Python in assembly 6502"""
        try:
            # 1. Parsing
            ast_tree = self.parser.parse(python_code)
            
            # 2. Generazione codice
            self.code_generator.visit_program(ast_tree)
            
            # 3. Aggiunta routine utilizzate
            self._add_required_routines()
            
            # 4. Generazione output
            assembly_code = self.output.generate()
            
            # 5. Ottimizzazione
            lines = assembly_code.split('\n')
            optimized_lines = self.optimizer.optimize(lines)
            
            return '\n'.join(optimized_lines)
            
        except Exception as e:
            raise CompilerError(f"Compilation failed: {str(e)}")
    
    def _add_required_routines(self):
        """Aggiunge le routine necessarie alla sezione routine"""
        # Marca le routine utilizzate nel generatore di codice
        for routine_name in self.code_generator.used_routines:
            self.routine_manager.mark_routine_used(routine_name)
        
        # Ottieni il codice delle routine
        routine_code = self.routine_manager.get_used_routines_code()
        
        # Aggiungile alla sezione routine
        self.output.switch_to_routines_section()
        self.output.add_lines(routine_code)
        
        # Aggiunge anche le variabili necessarie
        self._add_required_variables()
    
    def _add_required_variables(self):
        """Aggiunge le variabili necessarie per le routine"""
        self.output.switch_to_data_section()
        
        # Variabili per operazioni matematiche
        if "multiply16x16" in self.routine_manager.used_routines:
            self.output.add_lines([
                "MULT_ARG1:      .word 0",
                "MULT_ARG2:      .word 0",
                "MULT_RESULT:    .dword 0"
            ])
        
        if "divide16x16" in self.routine_manager.used_routines:
            self.output.add_lines([
                "DIV_DIVIDEND:   .word 0",
                "DIV_DIVISOR:    .word 0",
                "DIV_QUOTIENT:   .word 0",
                "DIV_REMAINDER:  .word 0"
            ])
        
        if "print_int16" in self.routine_manager.used_routines:
            self.output.add_lines([
                "PRINT_VALUE:    .word 0",
                "PRINT_BUFFER:   .res 8"
            ])
        
        # Variabili generali
        self.output.add_lines([
            "RETURN_VALUE:   .word 0",
            "FRAME_POINTER:  .byte 0"
        ])
        
        # Variabili temporanee
        for i in range(self.code_generator.temp_var_counter):
            self.output.add_line(f"TEMP_{i}:        .word 0")
        
        # Variabili globali del programma
        for var_name, variable in self.symbol_table.global_vars.items():
            if variable.data_type == DataType.INT16:
                self.output.add_line(f"{var_name}:        .word 0")
            elif variable.data_type == DataType.FLOAT32:
                self.output.add_line(f"{var_name}:        .dword 0")

# ============================================================================
# ESEMPIO D'USO
# ============================================================================

def example_usage():
    """Esempio di utilizzo del compiler"""
    
    # Codice Python di esempio
    python_code = """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def main():
    result = fibonacci(10)
    print(result)

main()
"""
    
    # Compilazione
    compiler = Py2C64Compiler()
    
    try:
        assembly_code = compiler.compile(python_code)
        print("Compilation successful!")
        print("Generated assembly:")
        print("=" * 50)
        print(assembly_code)
    except CompilerError as e:
        print(f"Compilation failed: {e}")

# ============================================================================
# TEST FRAMEWORK
# ============================================================================

class TestCase:
    """Rappresenta un caso di test"""
    
    def __init__(self, name: str, code: str, expected_output: Optional[str] = None):
        self.name = name
        self.code = code
        self.expected_output = expected_output

class TestRunner:
    """Esegue i test del compiler"""
    
    def __init__(self):
        self.compiler = Py2C64Compiler()
        self.test_cases: List[TestCase] = []
    
    def add_test_case(self, test_case: TestCase):
        """Aggiunge un caso di test"""
        self.test_cases.append(test_case)
    
    def run_tests(self) -> bool:
        """Esegue tutti i test"""
        passed = 0
        failed = 0
        
        for test_case in self.test_cases:
            try:
                result = self.compiler.compile(test_case.code)
                
                if test_case.expected_output:
                    if result.strip() == test_case.expected_output.strip():
                        print(f"✓ {test_case.name}: PASSED")
                        passed += 1
                    else:
                        print(f"✗ {test_case.name}: FAILED (output mismatch)")
                        failed += 1
                else:
                    print(f"✓ {test_case.name}: COMPILED")
                    passed += 1
                    
            except Exception as e:
                print(f"✗ {test_case.name}: FAILED ({e})")
                failed += 1
        
        print(f"\nResults: {passed} passed, {failed} failed")
        return failed == 0

# Test cases di esempio
def create_test_cases() -> List[TestCase]:
    """Crea casi di test di esempio"""
    return [
        TestCase(
            name="Simple Assignment",
            code="x = 42",
        ),
        TestCase(
            name="Arithmetic Operations",
            code="result = (10 + 20) * 3",
        ),
        TestCase(
            name="If Statement",
            code="""
if x > 0:
    print(x)
else:
    print(0)
""",
        ),
        TestCase(
            name="While Loop",
            code="""
i = 0
while i < 10:
    print(i)
    i = i + 1
""",
        ),
        TestCase(
            name="For Loop",
            code="""
for i in range(5):
    print(i)
""",
        ),
        TestCase(
            name="Function Definition",
            code="""
def add(a, b):
    return a + b

result = add(5, 3)
print(result)
""",
        ),
        TestCase(
            name="C64 Graphics",
            code="""
gfx_turn_on()
gfx_clear_screen()
draw_line(0, 0, 100, 100)
draw_circle(160, 100, 50)
""",
        ),
        TestCase(
            name="C64 Sprites",
            code="""
sprite_enable(0b00000001)
sprite_set_pos(0, 100, 100)
sprite_set_color(0, 1)
""",
        )
    ]

if __name__ == "__main__":
    # Esegui i test
    runner = TestRunner()
    
    for test_case in create_test_cases():
        runner.add_test_case(test_case)
    
    runner.run_tests()
    
    # Esempio di compilazione
    print("\n" + "=" * 60)
    print("EXAMPLE COMPILATION")
    print("=" * 60)
    example_usage()