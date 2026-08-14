"""Dump named CIL instructions from a managed assembly."""

from __future__ import annotations

import argparse
from pathlib import Path

import dnfile
from dncil.cil.body.reader import read_method_body_from_bytes
from dncil.clr.token import StringToken, Token


TABLES = {
    0x01: "TypeRef",
    0x02: "TypeDef",
    0x04: "Field",
    0x06: "MethodDef",
    0x0A: "MemberRef",
    0x11: "StandAloneSig",
    0x1B: "TypeSpec",
    0x2B: "MethodSpec",
}


def token_name(pe: dnfile.dnPE, token: Token) -> str:
    if isinstance(token, StringToken):
        value = pe.net.user_strings.get(token.rid)
        return repr(value.value if value else None)
    table_name = TABLES.get(token.table)
    if not table_name:
        return str(token)
    table = getattr(pe.net.mdtables, table_name, None)
    if not table or token.rid < 1 or token.rid > len(table.rows):
        return str(token)
    row = table.rows[token.rid - 1]
    name = getattr(row, "Name", None) or getattr(row, "TypeName", None)
    return f"{table_name}::{name}" if name else f"{table_name}[{token.rid}]"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("assembly", type=Path)
    parser.add_argument("type_name")
    parser.add_argument("methods", nargs="*")
    args = parser.parse_args()

    pe = dnfile.dnPE(str(args.assembly))
    wanted = set(args.methods)
    types = [row for row in pe.net.mdtables.TypeDef.rows if str(row.TypeName) == args.type_name]
    if not types:
        raise SystemExit(f"type not found: {args.type_name}")
    type_row = types[0]
    print(f"type {args.type_name}")
    print("fields:", ", ".join(str(index.row.Name) for index in type_row.FieldList))
    for index in type_row.MethodList:
        method = index.row
        name = str(method.Name)
        if wanted and name not in wanted:
            continue
        print(f"\n.method {name} rva=0x{method.Rva:X}")
        if not method.Rva:
            continue
        body = read_method_body_from_bytes(pe.get_data(method.Rva, 1_000_000))
        for instruction in body.instructions:
            operand = instruction.operand
            if isinstance(operand, Token):
                operand = token_name(pe, operand)
            suffix = "" if operand is None else f" {operand}"
            print(f"  IL_{instruction.offset:04X}: {instruction.opcode.name}{suffix}")


if __name__ == "__main__":
    main()
