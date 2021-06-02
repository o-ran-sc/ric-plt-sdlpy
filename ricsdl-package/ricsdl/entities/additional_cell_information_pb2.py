# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: additional_cell_information.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='additional_cell_information.proto',
  package='entities',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n!additional_cell_information.proto\x12\x08\x65ntities\"\xec\x01\n\x19\x41\x64\x64itionalCellInformation\x12\x15\n\rcell_latitude\x18\x01 \x01(\x02\x12\x16\n\x0e\x63\x65ll_longitude\x18\x02 \x01(\x02\x12\x16\n\x0e\x61ntenna_height\x18\x03 \x01(\x02\x12!\n\x19\x61ntenna_azimuth_direction\x18\x04 \x01(\x02\x12\x1a\n\x12\x61ntenna_tilt_angle\x18\x05 \x01(\x02\x12\x1c\n\x14\x61ntenna_max_transmit\x18\x06 \x01(\x02\x12\x18\n\x10\x61ntenna_max_gain\x18\x07 \x01(\x02\x12\x11\n\tsector_id\x18\x08 \x01(\rb\x06proto3')
)




_ADDITIONALCELLINFORMATION = _descriptor.Descriptor(
  name='AdditionalCellInformation',
  full_name='entities.AdditionalCellInformation',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='cell_latitude', full_name='entities.AdditionalCellInformation.cell_latitude', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cell_longitude', full_name='entities.AdditionalCellInformation.cell_longitude', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='antenna_height', full_name='entities.AdditionalCellInformation.antenna_height', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='antenna_azimuth_direction', full_name='entities.AdditionalCellInformation.antenna_azimuth_direction', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='antenna_tilt_angle', full_name='entities.AdditionalCellInformation.antenna_tilt_angle', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='antenna_max_transmit', full_name='entities.AdditionalCellInformation.antenna_max_transmit', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='antenna_max_gain', full_name='entities.AdditionalCellInformation.antenna_max_gain', index=6,
      number=7, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sector_id', full_name='entities.AdditionalCellInformation.sector_id', index=7,
      number=8, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=48,
  serialized_end=284,
)

DESCRIPTOR.message_types_by_name['AdditionalCellInformation'] = _ADDITIONALCELLINFORMATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

AdditionalCellInformation = _reflection.GeneratedProtocolMessageType('AdditionalCellInformation', (_message.Message,), dict(
  DESCRIPTOR = _ADDITIONALCELLINFORMATION,
  __module__ = 'additional_cell_information_pb2'
  # @@protoc_insertion_point(class_scope:entities.AdditionalCellInformation)
  ))
_sym_db.RegisterMessage(AdditionalCellInformation)


# @@protoc_insertion_point(module_scope)
