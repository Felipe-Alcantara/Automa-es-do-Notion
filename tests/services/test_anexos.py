from __future__ import annotations

import pytest

from felixo_notion_mcp.services.anexos import anexar_arquivo


class ClienteFake:
    def __init__(self, pagina=None):
        self._pagina = pagina or {"properties": {}}
        self.uploads = []
        self.atualizacoes = []

    def enviar_arquivo(self, conteudo, nome, content_type):
        self.uploads.append((nome, content_type, len(conteudo)))
        return "upload-1"

    def obter_pagina(self, page_id):
        return self._pagina

    def atualizar_pagina(self, page_id, props):
        self.atualizacoes.append((page_id, props))
        return {"id": page_id}


@pytest.fixture
def arquivo(tmp_path):
    caminho = tmp_path / "relatorio.docx"
    caminho.write_bytes(b"conteudo")
    return caminho


def test_anexa_arquivo_com_mime_e_propriedade(arquivo):
    cliente = ClienteFake()
    resumo = anexar_arquivo("pag1", arquivo, cliente=cliente)

    nome, content_type, tamanho = cliente.uploads[0]
    assert nome == "relatorio.docx"
    assert "wordprocessingml" in content_type
    assert tamanho == 8
    page_id, props = cliente.atualizacoes[0]
    assert page_id == "pag1"
    anexos = props["Arquivos e mídia"]["files"]
    assert anexos[0]["file_upload"]["id"] == "upload-1"
    assert resumo["total_anexos"] == 1


def test_preserva_anexos_existentes_por_padrao(arquivo):
    pagina = {
        "properties": {
            "Arquivos e mídia": {
                "files": [
                    {"type": "external", "name": "antigo.pdf", "external": {"url": "https://x"}},
                    {"type": "file", "name": "notion.png", "file": {"url": "https://tmp"}},
                ]
            }
        }
    }
    cliente = ClienteFake(pagina)
    resumo = anexar_arquivo("pag1", arquivo, cliente=cliente)

    anexos = cliente.atualizacoes[0][1]["Arquivos e mídia"]["files"]
    assert resumo["total_anexos"] == 3
    assert anexos[0]["external"]["url"] == "https://x"
    # arquivo hospedado pelo Notion é re-referenciado como external
    assert anexos[1] == {"type": "external", "name": "notion.png", "external": {"url": "https://tmp"}}
    assert anexos[2]["type"] == "file_upload"


def test_substituir_ignora_existentes(arquivo):
    pagina = {
        "properties": {
            "Anexos": {"files": [{"type": "external", "name": "a", "external": {"url": "u"}}]}
        }
    }
    cliente = ClienteFake(pagina)
    resumo = anexar_arquivo(
        "pag1", arquivo, propriedade="Anexos", substituir=True, cliente=cliente
    )
    assert resumo["total_anexos"] == 1


def test_arquivo_inexistente_levanta(tmp_path):
    with pytest.raises(ValueError, match="não encontrado"):
        anexar_arquivo("pag1", tmp_path / "nada.bin", cliente=ClienteFake())


def test_mime_nao_depende_do_registro_do_sistema(arquivo, monkeypatch):
    """No Windows o registro costuma não conhecer ``.docx``: a tabela própria decide."""

    monkeypatch.setattr("mimetypes.guess_type", lambda *_a, **_k: (None, None))
    cliente = ClienteFake()
    anexar_arquivo("pag1", arquivo, cliente=cliente)

    assert cliente.uploads[0][1] == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def test_mime_desconhecido_cai_em_octet_stream(tmp_path, monkeypatch):
    monkeypatch.setattr("mimetypes.guess_type", lambda *_a, **_k: (None, None))
    desconhecido = tmp_path / "dados.zzz"
    desconhecido.write_bytes(b"x")
    cliente = ClienteFake()
    anexar_arquivo("pag1", desconhecido, cliente=cliente)

    assert cliente.uploads[0][1] == "application/octet-stream"


def test_mime_da_tabela_vence_o_registro_do_sistema(arquivo, monkeypatch):
    monkeypatch.setattr("mimetypes.guess_type", lambda *_a, **_k: ("application/zip", None))
    cliente = ClienteFake()
    anexar_arquivo("pag1", arquivo, cliente=cliente)

    assert "wordprocessingml" in cliente.uploads[0][1]


@pytest.mark.parametrize(
    ("nome", "esperado"),
    [
        ("a.PDF", "application/pdf"),
        ("a.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("a.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
        ("a.csv", "text/csv"),
        ("a.md", "text/markdown"),
        ("a.webp", "image/webp"),
        ("a.svg", "image/svg+xml"),
        ("a.mp4", "video/mp4"),
        ("a.zip", "application/zip"),
    ],
)
def test_tabela_de_mime_cobre_extensoes_comuns(tmp_path, monkeypatch, nome, esperado):
    monkeypatch.setattr("mimetypes.guess_type", lambda *_a, **_k: (None, None))
    caminho = tmp_path / nome
    caminho.write_bytes(b"x")
    cliente = ClienteFake()
    anexar_arquivo("pag1", caminho, cliente=cliente)

    assert cliente.uploads[0][1] == esperado
