


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    # we took out all the spacee
    i = 0
    tokens = []
    while i < len(source):
        # print(i, source[i])
        if source[i] == ";":
            # once we hit a semicolon keep stepping until we find a line break
            while i < len(source) and source[i] != "\n":
                # print(source[i], "FHAIEO")
                i += 1
            if i >= len(source):
                break
            else:
                continue
        if source[i] == "(":
            tokens.append(source[i])
            i += 1
            continue
        if source[i] == ")":
            tokens.append(source[i])
            i += 1
            continue
        if source[i] == "\n":
            i += 1
            continue
        if source[i] != " ":
            start_index = i
            # once we hit a non parenthesis keep stepping till we hit a space
            while i < len(source) and source[i] not in " (  ) \n":
                i += 1
            tokens.append(source[start_index:i])
            continue
        i += 1
    return tokens


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """

    def parse_expression(index):
        if tokens[index] == ")":
            raise SchemeSyntaxError
        if tokens[index] == "(":
            index += 1
            subexpression = []
            try:
                while tokens[index] != ")":
                    if len(tokens) - 1 == index:
                        raise SchemeSyntaxError
                    next_val, index = parse_expression(index)
                    subexpression.append(next_val)
                return subexpression, (index + 1)
            except IndexError:
                raise SchemeSyntaxError
        else:
            return number_or_symbol(tokens[index]), index + 1

    answer, index = parse_expression(0)
    if len(tokens) != index:
        raise SchemeSyntaxError
    return answer
    # error check, if you don't get to the end of the expression


######################
# Built-in Functions #
######################


def product(products):
    answer = products[0]
    for multiplier in range(1, len(products)):
        answer *= products[multiplier]
    return answer


def division(divisers):
    answer = divisers[0]
    for diviser in range(1, len(divisers)):
        answer /= divisers[diviser]
    return answer


##############
# Evaluation #
##############


def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    # frame tings

    if frame is None:
        frame = Frame()

    if isinstance(tree, (float, int)):
        return tree

    elif isinstance(tree, str):
        return frame[tree]
    if len(tree) == 0:
        print("1")
        raise SchemeEvaluationError(f"evaluate functions check")
    elif tree[0] == "define":
        if isinstance(tree[1], list):
            # ['define', 'add2', ['lambda', ['x', 'y'], ['+', 'x', 'y']]]
            # ['define', ['add2', 'x', 'y'], ['+', 'x', 'y']]
            new_list = ["lambda"] + [tree[1][1:]]
            new_list.append(tree[2])
            new_tree = [tree[0], tree[1][0], new_list]
    
            return evaluate(new_tree, frame)
        result = evaluate(tree[2], frame)
        frame[tree[1]] = result
        return result

    elif tree[0] == "lambda":
      
        new_func = Function(frame, tree[1], tree[2])
        return new_func
    elif tree[0] == "if":
      
        if evaluate(tree[1], frame) == True:
            return evaluate(tree[2], frame)
        else:
            return evaluate(tree[3], frame)
    elif tree[0] == "and":
        for sub_tree in tree[1:]:
            if not evaluate(sub_tree, frame):
                return False
        return True
    elif tree[0] == "or":
        for sub_tree in tree[1:]:
            if evaluate(sub_tree, frame):
                return True
        return False
    elif tree[0] == "del":
        evaluate(tree[1], frame)
        return frame.delete(tree[1])
    elif tree[0] == "let":
        baby_frame = Frame(frame)
        for sub_tree in tree[1]:
            baby_frame.bindings[sub_tree[0]] = evaluate(sub_tree[1], baby_frame)
        return evaluate(tree[2], baby_frame)
    elif tree[0] == "set!":
        frame[tree[1]]
        temp = evaluate(tree[2], frame)
        frame.set_exisits(tree[1], temp)
        return temp

    else:
        eval_tree = []
        for element in tree:
            eval_tree.append(evaluate(element, frame))

        if not callable(eval_tree[0]):
            print("2")
            raise SchemeEvaluationError(f"Not callable")

        return eval_tree[0](eval_tree[1:])


def result_and_frame(tree, frame=None):
    if frame is None:
        frame = Frame()

    return (evaluate(tree, frame), frame)


class Frame:
    def __init__(self, parent_frame=None):
        if parent_frame is None:
            self.parent_frame = Builtin()

        else:
            self.parent_frame = parent_frame

        self.bindings = {}

    def __getitem__(self, var):
        if var in self.bindings:
            return self.bindings[var]

        return self.parent_frame[var]

    def __setitem__(self, var, val):
        self.bindings[var] = val

    def set_exisits(self, var, val):
        if var in self.bindings:
            self.bindings[var] = val
        else:
            self.parent_frame.set_exisits(var, val)

    def delete(self, val):
        if val not in self.bindings:
            raise SchemeNameError
        return self.bindings.pop(val)


class Builtin(Frame):
    def product(self, products):
        answer = products[0]
        for multiplier in range(1, len(products)):
            answer *= products[multiplier]
        return answer

    def division(self, divisers):
        answer = divisers[0]
        for diviser in range(1, len(divisers)):
            answer /= divisers[diviser]
        return answer

    def equal(self, equalizers):
        equalizer1 = equalizers[0]
        for equalizer in equalizers:
            if equalizer1 != equalizer:
                return False
        return True

    def greater(self, greaters):
        for i in range(1, len(greaters)):
            if greaters[i - 1] <= greaters[i]:
                return False
        return True

    def lesser(self, lessers):
        for i in range(1, len(lessers)):
            if lessers[i - 1] >= lessers[i]:
                return False
        return True

    def greatereq(self, greatereqs):
        for i in range(1, len(greatereqs)):
            if greatereqs[i - 1] < greatereqs[i]:
                return False
        return True

    def lessereq(self, lessereq):
        for i in range(1, len(lessereq)):
            if lessereq[i - 1] > lessereq[i]:
                return False
        return True

    def not_it(self, notters):
        if len(notters) != 1:
            print("3")
            raise SchemeEvaluationError(f"meow")
        return not notters[0]

    def cons(self, cons):
        if len(cons) != 2:
            print("4")
            raise SchemeEvaluationError(f"pair declaration")
        return Pair(cons[0], cons[1])

    def car(self, con):
        if len(con) != 1 or not isinstance(con[0], Pair):
            print("5")
            raise SchemeEvaluationError("car declaration")
        return con[0].car

    def cdr(self, con):  # con is list of length 1, with a Pair object
        # con => [Pair object]
        #
        if len(con) != 1 or not isinstance(con[0], Pair):
            print("6")
            raise SchemeEvaluationError("cdr declaration")
        return con[0].cdr

    def list(self, list_elements):
        list_object = Nill
        for list_element in reversed(list_elements):
            list_object = Pair(list_element, list_object)
        return list_object

    def islist(self, listy):
        # I GOT A CLUE ON THIS ONE BIG BRO
        if listy[0] == Nill:
            return True
        if len(listy) != 1 or not isinstance(listy[0], Pair):
            return False
        cdr = self.cdr(listy)
        cdr_list = [cdr]
        if isinstance(cdr, Pair):
            return self.islist(cdr_list)
        elif cdr == Nill:
            return True
        return False

    def list_length(self, listy):
        # list is the list of arguments, and the arguments is a linked list or Pair object
        # car is left side of Pair
        # cdr is right side of Pair
        if not self.islist(listy):
            print("7")
            raise SchemeEvaluationError("listlength")
        if listy[0] == Nill:
            return 0
        count = 1
        while self.cdr(listy) != Nill:
            count += 1
            listy = [self.cdr([listy[0]])]
        return count

    def list_indexing(self, listy):
        if self.islist([listy[0]]):
            # itteravely go into list'
            if listy[1] < self.list_length([listy[0]]):
                index = listy[1]
                linked_list = listy[0]
                while index != 0:
                    linked_list = self.cdr([linked_list])
                    index -= 1
                return self.car([linked_list])
        elif listy[1] == 0 and isinstance(listy[0], Pair):
            pair = [listy[0]]
            return self.car(pair)
        print('8')
        raise SchemeEvaluationError("indexing")

    def copy(self, listy):
        # given a list with a list in it return a deep copy of that list
        old_list = listy[0]
        if old_list == Nill:
            return Nill
        new_list = Pair(old_list.car, self.copy([old_list.cdr]))
        return new_list

    def map_func(self, listy):
        func = listy[0]
        old_list = listy[1]
        if old_list == Nill:
            return Nill
        new_list = Pair(
            func([self.car([old_list])]), self.map_func([func, self.cdr([old_list])])
        )
        return new_list

    def filter(self, listy):
        func = listy[0]
        old_list = listy[1]
        if old_list == Nill:
            return Nill
        elif func([self.car([old_list])]):
            return Pair(old_list.car, self.filter([func, old_list.cdr]))
        else:
            return self.filter([func, self.cdr([old_list])])

    def beign(self, listy):
        return listy[-1]

    def reduce(self, listy):
        func = listy[0]
        tree = listy[1]
        val = listy[2]
        if tree is Nill:
            return val
        return self.reduce([func, tree.cdr, func([val, tree.car])])

    def append(self, listy):
        if len(listy) == 0:
            return Nill
        if not self.islist([listy[0]]):
            print("9")
            raise SchemeEvaluationError("append 1")
        new_list = self.copy([listy[0]])
        end_of_list=new_list
        for additional_list in listy[1:]:
            if new_list == Nill:
                new_list = self.copy([additional_list])
                continue
            if additional_list == Nill:
                continue
            elif not self.islist([additional_list]):
                print("10")
                raise SchemeEvaluationError("append 2")
            else:
               
                # get to end of list
                while self.cdr([end_of_list]) != Nill:
                    end_of_list = self.cdr([end_of_list])
                # then just shove the new list at the end of list, APPENDING IT
             
                end_of_list.cdr = self.copy([additional_list])
        return new_list

    def __init__(self):
        self.bindings = {
            "+": sum,
            "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
            "*": self.product,
            "/": self.division,
            "#t": True,
            "#f": False,
            ">": self.greater,
            "<": self.lesser,
            ">=": self.greatereq,
            "<=": self.lessereq,
            "equal?": self.equal,
            "not": self.not_it,
            "cons": self.cons,
            "car": self.car,
            "cdr": self.cdr,
            "nil": Nill,
            "list": self.list,
            "list?": self.islist,
            "append": self.append,
            "length": self.list_length,
            "list-ref": self.list_indexing,
            "map": self.map_func,
            "filter": self.filter,
            "reduce": self.reduce,
            "begin": self.beign,
        }

    def __getitem__(self, name):
        if name in self.bindings:
            return self.bindings[name]

        raise SchemeNameError(f"Cannot find {name}")


def evaluate_file(file, frame=None):
    open_file = open(file, "r")
    open_file = parse(tokenize(open_file.read()))
    return evaluate(open_file, frame)


class Nill:
    def __init(self):
        pass


class Function:
    def __init__(self, frame, paramaters, code):
        self.frame = frame
        self.paramaters = paramaters
        self.code = code

    def __call__(self, arg):
        func_frame = Frame(self.frame)
        if len(self.paramaters) != len(arg):
            print("11")
            raise SchemeEvaluationError(f"Wrong num params.")
        for val, var in zip(arg, self.paramaters):
            func_frame[var] = val
        return evaluate(self.code, func_frame)


class Pair:
    def __init__(self, pair1, pair2):
        self.car = pair1
        self.cdr = pair2

    def __str__(self) -> str:
        string1 = ""
        string1 += "(" + str(self.car) + ", " + str(self.cdr) + ")"
        return string1


def repl(verbose=False, frame=None):
    """
    Read in a single line of user input, evaluate the expression, and print 
    out the result. Repeat until user inputs "QUIT"
    
    Arguments:
        verbose: optional argument, if True will display tokens and parsed
            expression in addition to more detailed error output.
    """
    import traceback

    if frame is None:
        _, frame = result_and_frame(["+"])  # make a global frame
    while True:
        input_str = input("in> ")
        if input_str == "QUIT":
            return
        try:
            token_list = tokenize(input_str)
            if verbose:
                print("tokens>", token_list)
            expression = parse(token_list)
            if verbose:
                print("expression>", expression)
            output, frame = result_and_frame(expression, frame)
            print("  out>", output)
        except SchemeError as e:
            if verbose:
                traceback.print_tb(e.__traceback__)
            print("Error>", repr(e))


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    # repl(True)
    # x = "(define circle-area (lambda (r) (* 3.14 (* r r))))"
    # print(
    #     parse(tokenize(x))
    #     == ["define", "circle-area", ["lambda", ["r"], ["*", 3.14, ["*", "r", "r"]]]]
    awesome_frame = None
    if len(sys.argv) > 1:
        awesome_frame = Frame()
        for thingy in sys.argv[1:]:
            evaluate_file(thingy, awesome_frame)
    repl(True, awesome_frame)
