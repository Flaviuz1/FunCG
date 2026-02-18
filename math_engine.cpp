#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cmath>
#include <string>
#include <vector>
#include <memory>
#include <stdexcept>
#include <unordered_map>
#include <functional>
#include <sstream>

using namespace std;
namespace py = pybind11;

static const int ESC = 100;                   // Taylor-series precision
static const int ISPTC = 10000;               // Integral / arctg precision
static const double M_E = 2.718281828459045;  // Euler's constant
static const double M_PI = 3.141592653589793; // PI

// Forward declarations
double power(double b, double p);
double logarithm(double b, double x);
double sin_c(double x);
double cos_c(double x);
double arcsin_c(double x);
double arctg_c(double x);

unordered_map<int, long long> factorial_memo = {{0, 1}, {1, 1}};
int factorial_memo_max = 1;

long long factorial(int x)
{
    if (x < 0)
        throw domain_error("factorial of negative number");
    auto it = factorial_memo.find(x);
    if (it != factorial_memo.end())
        return it->second;
    long long ans = factorial_memo[factorial_memo_max];
    for (int i = factorial_memo_max + 1; i <= x; ++i)
    {
        ans *= i;
        factorial_memo[i] = ans;
    }
    factorial_memo_max = x;
    return ans;
}

double absolute_val(double x) { return x < 0 ? -x : x; }

double floor_c(double x)
{
    int ans = 0;
    if (x >= 0)
    {
        while (ans + 1 <= x)
            ++ans;
    }
    else
    {
        while (ans - 1 >= x)
            --ans;
    }
    return (double)ans;
}

double ceiling_c(double x)
{
    double f = floor_c(x);
    return (x > f) ? f + 1 : f;
}

double integer_c(double x) { return x >= 0 ? floor_c(x) : ceiling_c(x); }

double _int_power(double base, int exp)
{
    double r = 1.0;
    for (int i = 0; i < exp; ++i)
        r *= base;
    return r;
}

double logarithm(double b, double x)
{
    if (x <= 0)
        throw domain_error("logarithm undefined for x <= 0");
    if (b == M_E)
    {
        if (x == 1.0)
            return 0.0;
        if (x >= 0.5 && x <= 1.5)
        {
            double t = x - 1.0, result = 0.0;
            for (int n = 1; n <= ESC; ++n)
            {
                double sign = ((n + 1) % 2 == 0) ? 1.0 : -1.0;
                result += sign * _int_power(t, n) / n;
            }
            return result;
        }
        else if (x > 1.5)
        {
            return 1.0 + logarithm(M_E, x / M_E);
        }
        else
        {
            return -logarithm(M_E, 1.0 / x);
        }
    }
    return logarithm(M_E, x) / logarithm(M_E, b);
}

double power(double b, double p)
{
    if (b == 1.0)
        return 1.0;
    if (p == 0.0)
        return 1.0;
    if (b == 0.0)
    {
        if (p > 0)
            return 0.0;
        throw domain_error("0^(negative) is undefined");
    }
    if (p == integer_c(p))
    {
        double ans = 1.0;
        int exp = (int)absolute_val(p);
        double base = (p > 0) ? b : 1.0 / b;
        for (int i = 0; i < exp; ++i)
            ans *= base;
        return ans;
    }
    if (b < 0)
        throw domain_error("Negative base with non-integer exponent");
    if (b == M_E)
    {
        double result = 0.0;
        for (int i = 0; i <= ESC; ++i)
            result += _int_power(p, i) / factorial(i);
        return result;
    }
    return power(M_E, p * logarithm(M_E, b));
}

double sin_c(double x)
{
    x = fmod(x, 2.0 * M_PI);
    double result = 0.0;
    for (int n = 0; n <= ESC; ++n)
    {
        double sign = (n % 2 == 0) ? 1.0 : -1.0;
        result += sign * _int_power(x, 2 * n + 1) / factorial(2 * n + 1);
    }
    return (absolute_val(result) < 1e-12) ? 0.0 : result;
}

double cos_c(double x)
{
    x = fmod(x, 2.0 * M_PI);
    double result = 0.0;
    for (int n = 0; n <= ESC; ++n)
    {
        double sign = (n % 2 == 0) ? 1.0 : -1.0;
        result += sign * _int_power(x, 2 * n) / factorial(2 * n);
    }
    return (absolute_val(result) < 1e-12) ? 0.0 : result;
}

double tg_c(double x)
{
    double s = sin_c(x), c = cos_c(x);
    if (absolute_val(c) < 1e-10)
        throw domain_error("tangent undefined (cos(x) ≈ 0)");
    return s / c;
}

double ctg_c(double x)
{
    double s = sin_c(x), c = cos_c(x);
    if (absolute_val(s) < 1e-10)
        throw domain_error("cotangent undefined (sin(x) ≈ 0)");
    return c / s;
}

double arcsin_c(double x)
{
    if (absolute_val(x) > 1)
        throw domain_error("arcsin undefined (|x| > 1)");
    if (x < 0)
        return -arcsin_c(-x);
    if (x > 0.9)
        return M_PI / 2.0 - arcsin_c(sqrt(1.0 - x));
    double result = 0.0;
    for (int n = 0; n <= ESC; ++n)
    {
        double num = (double)factorial(2 * n);
        double denom = _int_power(4.0, n) * power((double)factorial(n), 2) * (2 * n + 1);
        result += (num / denom) * power(x, 2 * n + 1);
    }
    return result;
}

double arccos_c(double x) { return M_PI / 2.0 - arcsin_c(x); }

double arctg_c(double x)
{
    if (absolute_val(x) <= 1.0)
    {
        double result = 0.0;
        for (int n = 0; n <= ISPTC; ++n)
        {
            double sign = (n % 2 == 0) ? 1.0 : -1.0;
            result += sign * _int_power(x, 2 * n + 1) / (2 * n + 1);
        }
        return result;
    }
    else if (x > 0)
    {
        return M_PI / 2.0 - arctg_c(1.0 / x);
    }
    else
    {
        return -M_PI / 2.0 - arctg_c(1.0 / x);
    }
}

double arcctg_c(double x) { return M_PI / 2.0 - arctg_c(x); }

// A(n, k) = n * (n-1) * ... * (n-k+1)  — arrangements
double arrangements(int n, int k)
{
    if (k < 0 || k > n)
        throw domain_error("arrangements: invalid n, k");
    double result = 1.0;
    for (int i = 0; i < k; ++i)
        result *= (n - i);
    return result;
}

// C(n, k) = n! / (k! * (n-k)!)  — combinations
double combinations(int n, int k)
{
    if (k < 0 || k > n)
        throw domain_error("combinations: invalid n, k");
    if (k == 0 || k == n)
        return 1.0;
    if (k > n - k)
        k = n - k; // use smaller side
    double result = 1.0;
    for (int i = 0; i < k; ++i)
    {
        result *= (n - i);
        result /= (i + 1);
    }
    return result;
}

int gcd(int a, int b)
{
    a = abs(a);
    b = abs(b);
    while (b)
    {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int lcm(int a, int b)
{
    int g = gcd(a, b);
    if (g == 0)
        throw domain_error("lcm: both arguments are zero");
    return abs(a) / g * abs(b);
}

double mod(double a, double b)
{
    if (b == 0)
        throw domain_error("mod: division by zero");
    return fmod(a, b);
}

double root(int n, double x)
{
    if (n == 0)
        throw domain_error("root: degree cannot be zero");
    if (x < 0 && n % 2 == 0)
        throw domain_error("root: even root of negative number");
    if (x < 0)
        return -power(-x, 1.0 / n);
    return power(x, 1.0 / n);
}

double stat_mean(const vector<double> &a)
{
    if (a.empty())
        throw domain_error("mean: no arguments");
    double sum = 0;
    for (double x : a)
        sum += x;
    return sum / a.size();
}

double stat_variance(const vector<double> &a)
{
    if (a.size() < 2)
        throw domain_error("variance: need at least 2 values");
    double m = stat_mean(a);
    double sum = 0;
    for (double x : a)
        sum += (x - m) * (x - m);
    return sum / a.size();
}

double stat_stdev(const vector<double> &a)
{
    return power(stat_variance(a), 0.5);
}

enum TokenType
{
    TOK_NUMBER,
    TOK_IDENT,
    TOK_OP,
    TOK_LPAREN,
    TOK_RPAREN,
    TOK_COMMA,
    TOK_END
};

struct Token
{
    TokenType type;
    double num_val;
    char op_val;
    string str_val;
};

vector<Token> tokenize(const string &expr)
{
    vector<Token> tokens;
    size_t i = 0;
    while (i < expr.size())
    {
        char c = expr[i];
        if (c == ' ' || c == '\t')
        {
            ++i;
            continue;
        }

        if (isdigit(c) || c == '.')
        {
            size_t start = i;
            while (i < expr.size() && (isdigit(expr[i]) || expr[i] == '.' ||
                                       expr[i] == 'e' || expr[i] == 'E' ||
                                       ((expr[i] == '+' || expr[i] == '-') && i > 0 &&
                                        (expr[i - 1] == 'e' || expr[i - 1] == 'E'))))
                ++i;
            Token t;
            t.type = TOK_NUMBER;
            t.num_val = stod(expr.substr(start, i - start));
            tokens.push_back(t);
            continue;
        }
        if (isalpha(c) || c == '_')
        {
            size_t start = i;
            while (i < expr.size() && (isalnum(expr[i]) || expr[i] == '_'))
                ++i;
            Token t;
            t.type = TOK_IDENT;
            t.str_val = expr.substr(start, i - start);
            tokens.push_back(t);
            continue;
        }
        if (c == '+' || c == '-' || c == '*' || c == '/' || c == '^' || c == '=')
        {
            Token t;
            t.type = TOK_OP;
            t.op_val = c;
            tokens.push_back(t);
            ++i;
            continue;
        }
        if (c == '(')
        {
            Token t;
            t.type = TOK_LPAREN;
            tokens.push_back(t);
            ++i;
            continue;
        }
        if (c == ')')
        {
            Token t;
            t.type = TOK_RPAREN;
            tokens.push_back(t);
            ++i;
            continue;
        }
        if (c == ',')
        {
            Token t;
            t.type = TOK_COMMA;
            tokens.push_back(t);
            ++i;
            continue;
        }

        throw runtime_error(string("Unexpected character: ") + c);
    }
    Token end;
    end.type = TOK_END;
    tokens.push_back(end);
    return tokens;
}

struct ASTNode
{
    virtual ~ASTNode() = default;
    virtual double eval(unordered_map<string, double> &vars) const = 0;
};
using NodePtr = unique_ptr<ASTNode>;

struct NumberNode : ASTNode
{
    double value;
    NumberNode(double v) : value(v) {}
    double eval(unordered_map<string, double> &) const override { return value; }
};

struct VariableNode : ASTNode
{
    string name;
    VariableNode(string n) : name(move(n)) {}
    double eval(unordered_map<string, double> &vars) const override
    {
        string lo = name;
        for (auto &ch : lo)
            ch = tolower(ch);
        if (lo == "pi")
            return M_PI;
        if (lo == "e")
            return M_E;
        if (lo == "inf")
            return 1e8;
        auto it = vars.find(lo);
        if (it != vars.end())
            return it->second;
        throw runtime_error("Variable '" + name + "' not defined");
    }
};

struct BinaryOpNode : ASTNode
{
    NodePtr left, right;
    char op;
    BinaryOpNode(NodePtr l, char o, NodePtr r)
        : left(move(l)), op(o), right(move(r)) {}
    double eval(unordered_map<string, double> &vars) const override
    {
        double l = left->eval(vars), r = right->eval(vars);
        switch (op)
        {
        case '+':
            return l + r;
        case '-':
            return l - r;
        case '*':
            return l * r;
        case '/':
            if (r == 0)
                throw domain_error("Division by zero");
            return l / r;
        case '^':
            return power(l, r);
        }
        throw runtime_error("Unknown operator");
    }
};

struct FunctionCallNode : ASTNode
{
    string name;
    vector<NodePtr> args;
    FunctionCallNode(string n, vector<NodePtr> a)
        : name(move(n)), args(move(a)) {}
    double eval(unordered_map<string, double> &vars) const override
    {
        string fn = name;
        for (auto &ch : fn)
            ch = tolower(ch);
        vector<double> a;
        for (auto &arg : args)
            a.push_back(arg->eval(vars));
        if (fn == "sin")
        {
            if (a.size() != 1)
                throw runtime_error("sin: 1 arg");
            return sin_c(a[0]);
        }
        if (fn == "cos")
        {
            if (a.size() != 1)
                throw runtime_error("cos: 1 arg");
            return cos_c(a[0]);
        }
        if (fn == "tan" || fn == "tg")
        {
            if (a.size() != 1)
                throw runtime_error("tan: 1 arg");
            return tg_c(a[0]);
        }
        if (fn == "ctg")
        {
            if (a.size() != 1)
                throw runtime_error("ctg: 1 arg");
            return ctg_c(a[0]);
        }
        if (fn == "arcsin")
        {
            if (a.size() != 1)
                throw runtime_error("arcsin: 1 arg");
            return arcsin_c(a[0]);
        }
        if (fn == "arccos")
        {
            if (a.size() != 1)
                throw runtime_error("arccos: 1 arg");
            return arccos_c(a[0]);
        }
        if (fn == "arctg" || fn == "arctan")
        {
            if (a.size() != 1)
                throw runtime_error("arctg: 1 arg");
            return arctg_c(a[0]);
        }
        if (fn == "arcctg")
        {
            if (a.size() != 1)
                throw runtime_error("arcctg: 1 arg");
            return arcctg_c(a[0]);
        }
        if (fn == "logarithm" || fn == "log")
        {
            if (a.size() == 1)
                return logarithm(M_E, a[0]);
            if (a.size() == 2)
                return logarithm(a[0], a[1]);
            throw runtime_error("logarithm: 1 or 2 args");
        }
        if (fn == "absolute" || fn == "abs")
        {
            if (a.size() != 1)
                throw runtime_error("absolute: 1 arg");
            return absolute_val(a[0]);
        }
        if (fn == "factorial")
        {
            if (a.size() != 1)
                throw runtime_error("factorial: 1 arg");
            return (double)factorial((int)a[0]);
        }
        if (fn == "floor")
        {
            if (a.size() != 1)
                throw runtime_error("floor: 1 arg");
            return floor_c(a[0]);
        }
        if (fn == "ceiling" || fn == "ceil")
        {
            if (a.size() != 1)
                throw runtime_error("ceiling: 1 arg");
            return ceiling_c(a[0]);
        }
        if (fn == "arrangements" || fn == "arra")
        {
            if (a.size() != 2)
                throw runtime_error("arrangements: 2 args (n, k)");
            return arrangements((int)a[0], (int)a[1]);
        }
        if (fn == "combinations" || fn == "comb")
        {
            if (a.size() != 2)
                throw runtime_error("combinations: 2 args (n, k)");
            return combinations((int)a[0], (int)a[1]);
        }
        if (fn == "permutations" || fn == "perm")
        {
            if (a.size() != 1)
                throw runtime_error("permutations: 1 arg (n)");
            return (double)factorial((int)a[0]);
        }
        if (fn == "gcd")
        {
            if (a.size() != 2)
                throw runtime_error("gcd: 2 args");
            return (double)gcd((int)a[0], (int)a[1]);
        }
        if (fn == "lcm")
        {
            if (a.size() != 2)
                throw runtime_error("lcm: 2 args");
            return (double)lcm((int)a[0], (int)a[1]);
        }
        if (fn == "mod")
        {
            if (a.size() != 2)
                throw runtime_error("mod: 2 args (a, b)");
            return mod(a[0], a[1]);
        }
        if (fn == "root")
        {
            if (a.size() != 2)
                throw runtime_error("root: 2 args (degree, x)");
            return root((int)a[0], a[1]);
        }
        if (fn == "mean")
        {
            if (a.empty())
                throw runtime_error("mean: at least 1 arg");
            return stat_mean(a);
        }
        if (fn == "variance")
        {
            if (a.size() < 2)
                throw runtime_error("variance: at least 2 args");
            return stat_variance(a);
        }
        if (fn == "stdev")
        {
            if (a.size() < 2)
                throw runtime_error("stdev: at least 2 args");
            return stat_stdev(a);
        }
        throw runtime_error("Unknown function: " + name);
    }
};

struct SigmaSumNode : ASTNode
{
    string var;
    NodePtr lower, upper, expr;
    SigmaSumNode(string v, NodePtr lo, NodePtr hi, NodePtr e)
        : var(v), lower(move(lo)), upper(move(hi)), expr(move(e)) {}
    double eval(unordered_map<string, double> &vars) const override
    {
        int lo = (int)lower->eval(vars), hi = (int)upper->eval(vars);
        double total = 0;
        for (int i = lo; i <= hi; ++i)
        {
            vars[var] = i;
            total += expr->eval(vars);
        }
        vars.erase(var);
        return total;
    }
};

struct ProductNode : ASTNode
{
    string var;
    NodePtr lower, upper, expr;
    ProductNode(string v, NodePtr lo, NodePtr hi, NodePtr e)
        : var(v), lower(move(lo)), upper(move(hi)), expr(move(e)) {}
    double eval(unordered_map<string, double> &vars) const override
    {
        int lo = (int)lower->eval(vars), hi = (int)upper->eval(vars);
        double prod = 1;
        for (int i = lo; i <= hi; ++i)
        {
            vars[var] = i;
            prod *= expr->eval(vars);
        }
        vars.erase(var);
        return prod;
    }
};

struct IntegralNode : ASTNode
{
    string var;
    NodePtr lower, upper, expr;
    IntegralNode(string v, NodePtr lo, NodePtr hi, NodePtr e)
        : var(v), lower(move(lo)), upper(move(hi)), expr(move(e)) {}
    double eval(unordered_map<string, double> &vars) const override
    {
        double a = lower->eval(vars), b = upper->eval(vars);
        double h = (b - a) / ISPTC;
        double total = 0;
        for (int i = 0; i < ISPTC; ++i)
        {
            double x0 = a + i * h, x1 = x0 + h;
            vars[var] = x0;
            double f0 = expr->eval(vars);
            vars[var] = x1;
            double f1 = expr->eval(vars);
            total += (f0 + f1) * h / 2.0;
        }
        vars.erase(var);
        return total;
    }
};

struct LimitNode : ASTNode
{
    string var;
    NodePtr to, expr;
    LimitNode(string v, NodePtr t, NodePtr e)
        : var(v), to(move(t)), expr(move(e)) {}
    double eval(unordered_map<string, double> &vars) const override
    {
        double t = to->eval(vars);
        double eps = 1e-6;
        vars[var] = t - eps;
        double left = expr->eval(vars);
        vars[var] = t + eps;
        double right = expr->eval(vars);
        vars.erase(var);
        if (abs(left - right) < 1e-4 &&
            abs(left) < 1e10 && abs(right) < 1e10)
            return (left + right) / 2.0;
        throw runtime_error("Limit does not exist (left/right limits differ)");
    }
};

class Parser
{
    vector<Token> tokens;
    size_t pos;

    Token &peek() { return tokens[pos]; }
    Token advance() { return tokens[pos++]; }

    Token expect(TokenType t, const string &msg = "")
    {
        if (peek().type != t)
            throw runtime_error("Syntax error: " + (msg.empty() ? "unexpected token" : msg));
        return advance();
    }

    NodePtr parse_expression()
    {
        auto node = parse_term();
        while (peek().type == TOK_OP && (peek().op_val == '+' || peek().op_val == '-'))
        {
            char op = advance().op_val;
            node = make_unique<BinaryOpNode>(move(node), op, parse_term());
        }
        return node;
    }

    NodePtr parse_term()
    {
        auto node = parse_factor();
        while (peek().type == TOK_OP && (peek().op_val == '*' || peek().op_val == '/'))
        {
            char op = advance().op_val;
            node = make_unique<BinaryOpNode>(move(node), op, parse_factor());
        }
        return node;
    }

    NodePtr parse_factor()
    {
        auto node = parse_power();
        while (peek().type == TOK_OP && peek().op_val == '^')
        {
            advance();
            node = make_unique<BinaryOpNode>(move(node), '^', parse_power());
        }
        return node;
    }

    NodePtr parse_power()
    {
        if (peek().type == TOK_OP && peek().op_val == '-')
        {
            advance();
            return make_unique<BinaryOpNode>(
                make_unique<NumberNode>(0), '-', parse_atom());
        }
        return parse_atom();
    }

    vector<NodePtr> parse_arguments()
    {
        vector<NodePtr> args;
        while (true)
        {
            args.push_back(parse_expression());
            if (peek().type == TOK_COMMA)
            {
                advance();
                continue;
            }
            break;
        }
        return args;
    }

    string get_var_name(NodePtr &node)
    {
        if (auto *v = dynamic_cast<VariableNode *>(node.get()))
            return v->name;
        throw runtime_error("Expected variable name as first argument");
    }

    NodePtr parse_atom()
    {
        Token tok = peek();
        if (tok.type == TOK_NUMBER)
        {
            advance();
            return make_unique<NumberNode>(tok.num_val);
        }
        if (tok.type == TOK_IDENT)
        {
            advance();
            string name = tok.str_val;
            if (peek().type == TOK_LPAREN)
            {
                advance(); // consume (
                auto args = parse_arguments();
                expect(TOK_RPAREN, "Expected ')'");

                string fn = name;
                for (auto &c : fn)
                    c = tolower(c);

                if (fn == "sum")
                {
                    if (args.size() != 4)
                        throw runtime_error("sum: needs 4 args");
                    string var = get_var_name(args[0]);
                    return make_unique<SigmaSumNode>(var, move(args[1]), move(args[2]), move(args[3]));
                }
                if (fn == "product")
                {
                    if (args.size() != 4)
                        throw runtime_error("product: needs 4 args");
                    string var = get_var_name(args[0]);
                    return make_unique<ProductNode>(var, move(args[1]), move(args[2]), move(args[3]));
                }
                if (fn == "integral")
                {
                    if (args.size() != 4)
                        throw runtime_error("integral: needs 4 args");
                    string var = get_var_name(args[0]);
                    return make_unique<IntegralNode>(var, move(args[1]), move(args[2]), move(args[3]));
                }
                if (fn == "lim")
                {
                    if (args.size() != 3)
                        throw runtime_error("lim: needs 3 args");
                    string var = get_var_name(args[0]);
                    return make_unique<LimitNode>(var, move(args[1]), move(args[2]));
                }
                return make_unique<FunctionCallNode>(name, move(args));
            }
            return make_unique<VariableNode>(name);
        }
        if (tok.type == TOK_LPAREN)
        {
            advance();
            auto node = parse_expression();
            expect(TOK_RPAREN, "Expected ')'");
            return node;
        }
        throw runtime_error("Unexpected token in expression");
    }

public:
    Parser(vector<Token> t) : tokens(move(t)), pos(0) {}

    NodePtr parse()
    {
        auto node = parse_expression();
        if (peek().type != TOK_END)
            throw runtime_error("Unexpected token at end of expression");
        return node;
    }
};

// Shared helper — parse and return AST
NodePtr build_ast(const string &expr)
{
    auto tokens = tokenize(expr);
    return Parser(move(tokens)).parse();
}

double evaluate_expr(const string &expr)
{
    auto ast = build_ast(expr);
    unordered_map<string, double> vars;
    return ast->eval(vars);
}

double evaluate_at(const string &expr, double x)
{
    auto ast = build_ast(expr);
    unordered_map<string, double> vars = {{"x", x}};
    return ast->eval(vars);
}

// Returns {x_values, y_values} as two parallel vectors; invalid points are NaN
pair<vector<double>, vector<double>>
evaluate_for_graph(const string &expr, double x_min, double x_max, int num_points)
{
    auto ast = build_ast(expr);
    vector<double> xs(num_points), ys(num_points);
    for (int i = 0; i < num_points; ++i)
    {
        double x = x_min + (x_max - x_min) * i / num_points;
        xs[i] = x;
        try
        {
            unordered_map<string, double> vars = {{"x", x}};
            double y = ast->eval(vars);
            ys[i] = (isfinite(y)) ? y : numeric_limits<double>::quiet_NaN();
        }
        catch (...)
        {
            ys[i] = numeric_limits<double>::quiet_NaN();
        }
    }
    return {xs, ys};
}

PYBIND11_MODULE(math_engine, m)
{
    m.doc() = "FunCG math engine — C++ backend";

    m.def("evaluate", &evaluate_expr,
          "Evaluate a math expression string and return a double",
          py::arg("expr"));

    m.def("evaluate_at", &evaluate_at,
          "Evaluate f(x) at a single x value",
          py::arg("expr"), py::arg("x"));

    m.def("evaluate_for_graph", &evaluate_for_graph,
          "Evaluate f(x) over a range, returns (x_list, y_list). "
          "Invalid points are NaN.",
          py::arg("expr"),
          py::arg("x_min") = -10.0,
          py::arg("x_max") = 10.0,
          py::arg("num_points") = 1000);
}
