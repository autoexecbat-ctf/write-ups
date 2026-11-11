"""Load the game's protobuf descriptors (dumped from CTFGame.Networking.Wire.dll) at runtime.

Usage:
    from protolib import msg, dump_protos
    Req = msg('game.v1.Request')
"""
import glob
import os
import sys

from google.protobuf import descriptor_pb2, descriptor_pool, message_factory

HERE = os.path.dirname(os.path.abspath(__file__))
PROTO_DIR = os.path.join(HERE, '..', 'assets_extracted', 'protos')

pool = descriptor_pool.DescriptorPool()
_fds = {}
for p in glob.glob(os.path.join(PROTO_DIR, '*.pb')):
    fd = descriptor_pb2.FileDescriptorProto()
    fd.ParseFromString(open(p, 'rb').read())
    _fds[fd.name] = fd

_added = set()


def _add(name):
    if name in _added:
        return
    fd = _fds.get(name)
    if fd is None:
        # well-known types
        from google.protobuf import timestamp_pb2, duration_pb2, empty_pb2, struct_pb2, wrappers_pb2, any_pb2  # noqa
        from google.protobuf import descriptor_pool as dp
        d = dp.Default().FindFileByName(name)
        p = descriptor_pb2.FileDescriptorProto()
        d.CopyToProto(p)
        fd = p
    for dep in fd.dependency:
        _add(dep)
    pool.Add(fd)
    _added.add(name)


for n in list(_fds):
    _add(n)


def msg(full_name):
    return message_factory.GetMessageClass(pool.FindMessageTypeByName(full_name))


TYPES = {1: 'double', 2: 'float', 3: 'int64', 4: 'uint64', 5: 'int32', 6: 'fixed64', 7: 'fixed32', 8: 'bool',
         9: 'string', 12: 'bytes', 13: 'uint32', 15: 'sfixed32', 16: 'sfixed64', 17: 'sint32', 18: 'sint64'}


def _fmt_msg(m, ind):
    out = [f"{ind}message {m.name} {{"]
    for e in m.enum_type:
        out.append(f"{ind}  enum {e.name} {{ " + ' '.join(f"{v.name}={v.number};" for v in e.value) + " }")
    for n in m.nested_type:
        out += _fmt_msg(n, ind + '  ')
    for f in m.field:
        t = TYPES.get(f.type, f.type_name)
        lab = 'repeated ' if f.label == 3 else ''
        oo = f" [oneof {m.oneof_decl[f.oneof_index].name}]" if f.HasField('oneof_index') else ''
        out.append(f"{ind}  {lab}{t} {f.name} = {f.number};{oo}")
    out.append(f"{ind}}}")
    return out


def dump_protos():
    for name, fd in sorted(_fds.items()):
        print(f"// ===== {name} (package {fd.package})")
        for e in fd.enum_type:
            print(f"enum {e.name} {{ " + ' '.join(f"{v.name}={v.number};" for v in e.value) + " }")
        for m in fd.message_type:
            print('\n'.join(_fmt_msg(m, '')))
        for s in fd.service:
            print(f"service {s.name} {{")
            for meth in s.method:
                print(f"  rpc {meth.name}({meth.input_type}) returns ({meth.output_type});")
            print("}")


if __name__ == '__main__':
    dump_protos()
