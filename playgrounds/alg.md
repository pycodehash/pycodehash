algorithm hash source code

in: 
- source code function
- first party/fqn prefix
out: hash
---
label: inliner

(optional)
idx: LocalCallVisitor
in:
- function: foo.src
func: find at least 1 call in foo
out: 
- call_found (bool): call found

If not call_found:
    goto wrap-up

Where is the call coming from?
Get the scope. Defined as: variable `x` refers to fqn `y` at a given step of the program `z` (`z` is call time).
Note: we don't know yet if import is module, class or func



[START FQN]
idx: BuildinScopeVisitor
in: 
- python version: py38
func: return global scope
out: buildin scope

idx: ModuleScopeVisitor
in:
- module file: src.py (from bar)
func: 
  - passed over (global) imports
  - GOTO IMPORT MODULE
  - check function definitions
  - check class definitions
  - checks scope reference at function call
  - REPLACE calls with current scope FQN
  out: scope

Is the reference overwritten locally?

idx: LocalScopeVisitor
in:
- function: foo.src
  - scope: (from previous)
  func:
  - pass over local imports
  - check local function definitions
  - check class definitions
  - check scope reference before function call
  - REPLACE calls with current scope FQN

idx: NestedScopeVisitor
in: func
...
out: ...

[END FQN]
idx: ScopeFilter
in: 
- calls (FQNs)
- known first party
func: filter out FQNs that should not be considered
out: filtered calls

idx: Deduplicated
in: list of FQNS
out: set of FQNs

[HERE]

idx: TypeResolver
in: scope
func: check the type of scope
out: module, func, class

idx: SourceLookup
in: call FQN, call type
func: 
- get source from function body  if function
- get source from class          if method
- get source from file           if module
out: source

hash = goto: inliner

idx: ReplaceFunc
in: call
func: replace func with FQN
out: source

label: wrap-up

idx: PostProcessAST
in: source
func:
- parse ast
- run postprocessing (strip comments, remove func name etc.)
- unpase ast
out: processed source

idx: PostProcessLines
in: processed source
func:
- split lines
- run postprocessing (platform line endings)
- join lines
out: processed source 2

idx: PrependModule
in: processed source 2
func: 
- prepend module namespace (comment) to code
out: processed source 3

idx: HashSource
in: processed source 3
func: hash source 
out: hash
