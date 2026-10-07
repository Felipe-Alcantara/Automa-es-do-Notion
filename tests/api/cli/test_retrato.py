import argparse
import json

from felixo_notion_mcp.api.cli.retrato import retratar_parser


def _parser():
    p = argparse.ArgumentParser(prog="x")
    sub = p.add_subparsers(dest="comando")
    el = sub.add_parser("editar-linha", aliases=["el"])
    el.add_argument("pagina_id")
    el.add_argument("--set", action="append", dest="valores")
    el.add_argument("--sim", action="store_true")
    return p


def test_retrato_registra_subcomandos_aliases_e_argumentos():
    r = retratar_parser(_parser())
    assert set(r["subcomandos"]) == {"editar-linha", "el"}
    args = {a["destino"]: a for a in r["subcomandos"]["editar-linha"]["argumentos"]}
    assert args["pagina_id"]["opcoes"] == []
    assert args["valores"]["opcoes"] == ["--set"]
    assert args["valores"]["acao"] == "_AppendAction"
    assert args["sim"]["padrao"] == "False"


def test_retrato_e_deterministico_e_serializavel():
    a = json.dumps(retratar_parser(_parser()), sort_keys=True)
    b = json.dumps(retratar_parser(_parser()), sort_keys=True)
    assert a == b


def _inteiro_positivo(texto):
    valor = int(texto)
    if valor <= 0:
        raise argparse.ArgumentTypeError("deve ser positivo")
    return valor


def test_retrato_registra_se_subcomando_e_obrigatorio_e_seu_destino():
    p = argparse.ArgumentParser(prog="x")
    sub = p.add_subparsers(dest="comando", required=True)
    app = sub.add_parser("app")
    app_sub = app.add_subparsers()  # sem dest e sem required
    app_sub.add_parser("start")
    r = retratar_parser(p)
    assert r["subcomandos_obrigatorio"] is True
    assert r["subcomandos_destino"] == "comando"
    app_r = r["subcomandos"]["app"]
    assert app_r["subcomandos_obrigatorio"] is False
    assert app_r["subcomandos_destino"] is None
    # parser sem subcomandos: nada obrigatório e sem destino
    folha = app_r["subcomandos"]["start"]
    assert folha["subcomandos_obrigatorio"] is False
    assert folha["subcomandos_destino"] is None


def test_retrato_registra_o_tipo_de_cada_argumento():
    p = argparse.ArgumentParser(prog="x")
    p.add_argument("posicional")
    p.add_argument("--limite", type=int)
    p.add_argument("--passo", type=_inteiro_positivo)
    p.add_argument("--sim", action="store_true")
    r = retratar_parser(p)
    tipos = {a["destino"]: a["tipo"] for a in r["argumentos"]}
    assert tipos["posicional"] is None
    assert tipos["limite"] == "int"
    assert tipos["passo"] == "_inteiro_positivo"
    assert tipos["sim"] is None


def test_retrato_registra_grupos_mutuamente_exclusivos_em_ordem_estavel():
    p = argparse.ArgumentParser(prog="x")
    g_b = p.add_mutually_exclusive_group(required=True)
    g_b.add_argument("--zeta")
    g_b.add_argument("--beta")
    g_a = p.add_mutually_exclusive_group()
    g_a.add_argument("--omega")
    g_a.add_argument("--alfa")
    p.add_argument("--solto")
    r = retratar_parser(p)
    assert r["exclusivos"] == [
        {"obrigatorio": False, "destinos": ["alfa", "omega"]},
        {"obrigatorio": True, "destinos": ["beta", "zeta"]},
    ]
    # parser sem grupos exclusivos
    q = argparse.ArgumentParser(prog="y")
    q.add_argument("--x")
    assert retratar_parser(q)["exclusivos"] == []
