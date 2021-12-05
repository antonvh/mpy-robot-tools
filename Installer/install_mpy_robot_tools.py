import ubinascii, os, machine,uhashlib
from ubinascii import hexlify

encoded=(('pyhuskylens.mpy', ('TQUCHyCLfOwQUgAHQi4uL21weV9yb2JvdF90b29scy9weWh1c2t5bGVucy5weTkoMDkjVHRlJUWAHR8fHytmJCQkJCQkJCREJCRkIIsUixKLrgCAEBBzbGVlcF9tcxAQdGlja3NfbXMqAhsIdGltZRwFFgEcBRYBWYBRGwxzdHJ1Y3QWAYAQAEgqARsAcxwASBYASFmAEAphdGFuMhAOZGVncmVlcyoCGwhtYXRoHAUWARwFFgFZSBMAgBAIcG9ydCoBGwZodWIcAxYBWUoVAFmAEBRVQVJURGV2aWNlKgEbJHB5YnJpY2tzLmlvZGV2aWNlcxwDFgFZSgEAXTICFghieXRlIwAWDEhFQURFUiMBFgxGQUlMRUQyAxEAfKAiPjQCNAEwHhYOUkVRVUVTVBYcUkVRVUVTVF9CTE9DS1MWHFJFUVVFU1RfQVJST1dTFh5SRVFVRVNUX0xFQVJORUQWLFJFUVVFU1RfQkxPQ0tTX0xFQVJORUQWLFJFUVVFU1RfQVJST1dTX0xFQVJORUQWGlJFUVVFU1RfQllfSUQWKFJFUVVFU1RfQkxPQ0tTX0JZX0lEFihSRVFVRVNUX0FSUk9XU19CWV9JRBYWUkVUVVJOX0lORk8WGFJFVFVSTl9CTE9DSxYYUkVUVVJOX0FSUk9XFhpSRVFVRVNUX0tOT0NLFiJSRVFVRVNUX0FMR09SSVRITRYSUkVUVVJOX09LFiZSRVFVRVNUX0NVU1RPTU5BTUVTFhpSRVFVRVNUX1BIT1RPFiRSRVFVRVNUX1NFTkRfUEhPVE8WLlJFUVVFU1RfU0VORF9LTk9XTEVER0VTFjRSRVFVRVNUX1JFQ0VJVkVfS05PV0xFREdFUxYmUkVRVUVTVF9DVVNUT01fVEVYVBYkUkVRVUVTVF9DTEVBUl9URVhUFhpSRVFVRVNUX0xFQVJOFhxSRVFVRVNUX0ZPUkdFVBYuUkVRVUVTVF9TRU5EX1NDUkVFTlNIT1QWLlJFUVVFU1RfU0FWRV9TQ1JFRU5TSE9UFjxSRVFVRVNUX0xPQURfQUlfRlJBTUVfRlJPTV9VU0IWHFJFUVVFU1RfSVNfUFJPFjBSRVFVRVNUX0ZJUk1XQVJFX1ZFUlNJT04WFlJFVFVSTl9CVVNZEQUWGlJFVFVSTl9JU19QUk+AFjRBTEdPUklUSE1fRkFDRV9S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\n'), '9a5ba7d8e1959169f9f36f3d46a1ecd149602bb76cdc109f4f2931e5e70d42c8'), ('__init__.mpy', ('TQUCHyAkAAoABzwuLi9tcHlfcm9ib3RfdG9vbHMvX19pbml0X18ucHkAUWMAAA==\n',), 'bd0eb1ec00392c81347ab95950ebc33661aa1cb23009054638ed4cbea66fcc3e'), ('bt.mpy', ('TQUCHyCTbHiwAgAHMC4uL21weV9yb2JvdF90b29scy9idC5weTkoKDAwUCAnJycnJycnJycnJycnJ2wkJCQkJCQkJGRAbiQkJCQkJCQkJCQkZyQkJCYmJiYmJyYmhxgtLS0tLWkgaSBDbW4gjSCFCmVAhQqL74soAIAQDmRpc3BsYXkQCkltYWdlKgIbBmh1YhwFFgEcBRYBWYBRGxJibHVldG9vdGgWAYBRGwxzdHJ1Y3QWAYAQEHNsZWVwX21zKgEbCHRpbWUcAxYBWYAQAEgqARsAcxwASBYASFmAEApUaW1lcioBGw5tYWNoaW5lHAMWAVkRDSMANAERASMBNAERASMCNAERASMDNAERASMENAERASMFNAERASMGNAERASMHNAERASMINAERASMJNAERASMKNAERASMLNAERASMMNAERASMNNAERASMONAErDxYeX0NPTk5FQ1RfSU1BR0VTgBYWTF9TVElDS19IT1KBFhZMX1NUSUNLX1ZFUoIWFlJfU1RJQ0tfSE9SgxYWUl9TVElDS19WRVKEFhJMX1RSSUdHRVKFFhJSX1RSSUdHRVKGFhBTRVRUSU5HMYcWEFNFVFRJTkcyiBYOQlVUVE9OUyMPEQBMESE0Ad1EM4CDFiBfSVJRX0dBVFRTX1dSSVRFhRYgX0lSUV9TQ0FOX1JFU1VMVIYWHF9JUlFfU0NBTl9ET05FhxYuX0lSUV9QRVJJUEhFUkFMX0NPTk5FQ1SIFjRfSVJRX1BFUklQSEVSQUxfRElTQ09OTkVDVIkWMl9JUlFfR0FUVENfU0VSVklDRV9SRVNVTFSLFkBfSVJRX0dBVFRDX0NIQVJBQ1RFUklTVElDX1JFU1VMVI8WLF9JUlFfR0FUVENfUkVBRF9SRVNVTFSSFiJfSVJRX0dBVFRDX05PVElGWYwWPF9JUlFfR0FUVENfQ0hBUkFDVEVSSVNUSUNfRE9ORYoWLl9JUlFfR0FUVENfU0VSVklDRV9ET05FkRYqX0lSUV9HQVRUQ19XUklURV9ET05FQkSAhBYXkBYXoBYXIoBAFhcigQAWFyKCABYXIoQAFhcikAAWFyKAwAAWFyKgABYXIoQAFhcihIAAFhcRGRQIVVVJRCMQNgEWFF9VQVJUX1VVSUQRBRQFIxE2ARYaX1VBUlRfVFhfVVVJRBEFFAUjEjYBFhpfVUFS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a1GwGBxfY29ubl9jYWxsYmFja1GwGCJfZGlzY29ubl9jYWxsYmFja1GwGCxfY2VudHJhbF9jb25uX2NhbGxiYWNrUbAYMl9jZW50cmFsX2Rpc2Nvbm5fY2FsbGJhY2tRsBgqX2NoYXJfcmVzdWx0X2NhbGxiYWNrUbAYHF9yZWFkX2NhbGxiYWNrLACwGCBfd3JpdGVfY2FsbGJhY2tzUbAYIF9ub3RpZnlfY2FsbGJhY2tRsBgYX3NlYXJjaF9uYW1lULAYHmNvbm5lY3RpbmdfdWFydFCwGB5jb25uZWN0aW5nX2xlZ29RYwAAAIl4oYCAQBAIaW5mbx+AxCcAsBMjRAiAEgB7sVM1AFlRYwAAAImbPNcQtAIlBYDIKCgtJy5HUSVKJycoJSolLi4uJ44IKCcqLClVRSdLSCYlTkgmJ0tIJ2gpI1GHDUgqJygpKCk2JSduYEgoaSdPaChdUyYmKSsnSyYmSSdLKEYqLW8AsRIgX0lSUV9TQ0FOX1JFU1VMVNlEuoCyMAXDxMXGxxIWZGVjb2RlX25hbWW3NAFFA4AQAj/IEh5kZWNvZGVfc2VydmljZXO3NAHJsBQPEA5Gb3VuZDoguCMDuTYEWbATFUQngLiwExfZRB6AEhRfVUFSVF9VVUlEud1EFoCzsBgUX2FkZHJfdHlwZRIAQrQ0AbAYCl9hZGRysBQSc3RvcF9zY2FuNgBZsBMfREaAEiRfTEVHT19TRVJWSUNFX1VVSUS53UQ+gLOwGAkSAEK0NAGwGAm1sBgSX2Fkdl90eXBlsBMSX19kZWNvZGVyFB23NgGwGApfbmFtZbATBRQdtzYBsBgSX3NlcnZpY2VzsBMFFCZkZWNvZGVfbWFudWZhY3R1cmVytzYBsBgSX21hbl9kYXRhsBMqX3NjYW5fcmVzdWx0X2NhbGxiYWNrRAuAsBQBs7S4uTYEWUKwgbESHF9JUlFfU0NBTl9ET05F2URSgLATI0Q5gLATGVHe00QqgBIAeyMEsBMjNAJZEhBzbGVlcF9tcyKDdDQBWbATCF9ibGUUFmdhcF9jb25uZWN0sBMJsBMhNgJZQgWAULAYDbATJl9zY2FuX2RvbmVfY2FsbGJhY2tECICwFAGyNgFZQlaBsRIuX0lSUV9QRVJJUEhFUkFMX0NPTk5FQ1TZRBmAsjADysPEurAYGF9jb25uX2hhbmRsZbATDxQuZ2F0dGNfZGlzY292ZXJfc2VydmljZXO6NgFZQjWBsRI0X0lSUV9QRVJJUEhFUkFMX0RJU0NPTk5FQ1TZRBiAsjADysvLsBMiX2Rpc2Nvbm5fY2FsbGJhY2tECICwFAG6NgFZQhWBsRIyX0lSUV9HQVRUQ19TRVJWSUNFX1JFU1VMVNlEM4CyMATKzM3OvhI32UQhgBIbIoN0NAFZSBAAsBMNFDxnYXR0Y19kaXNjb3Zlcl9jaGFyYWN0ZXJpc3RpY3O6vL02A1lKBQBZSgEAXULagLESQF9JUlFfR0FUVENfQ0hBUkFDVEVSSVNUSUM=\n', 'X1JFU1VMVNlEY4CyMAXKzyYQJhHOsBMZRD2AvhIaX1VBUlRfUlhfVVVJRNlECYAkELAYFF9yeF9oYW5kbGVCEYC+EhpfVUFSVF9UWF9VVUlE2UQJgCQQsBgUX3R4X2hhbmRsZUIAgBIAOrATHbATB7ATBSoDNAFEBYBQsBgLsBMqX2NoYXJfcmVzdWx0X2NhbGxiYWNrRAuAsBQBuiQQvjYDWUJvgLESIl9JUlFfR0FUVENfTk9USUZZ2UQngLIwA8omECYSEgBCJBI0ASYSsBMgX25vdGlmeV9jYWxsYmFja0QMgLAUAbokECQSNgNZQkCAsRIsX0lSUV9HQVRUQ19SRUFEX1JFU1VMVNlEOICyMAPKJhAmE7qwEw/ZRCSAJBCwEw+wExhfYnV0YV9oYW5kbGWwExhfYnV0Yl9oYW5kbGUqA91EEICwFBxfcmVhZF9jYWxsYmFjayQQEgBCJBM0ATYCWUIAgLGB2UQsgLIwA8rDxBIAeyMFujQCWbATJl9jb25uZWN0ZWRfY2VudHJhbHMUBmFkZLo2AVmwEyxfY2VudHJhbF9jb25uX2NhbGxiYWNrRAiAsBQBsjYBWUJrgLGC2UQhgLIwA8rDxBIAeyMGujQCWbATMl9jZW50cmFsX2Rpc2Nvbm5fY2FsbGJhY2tECICwFAGyNgFZQkSAsRIgX0lSUV9HQVRUU19XUklURdlELICyMALKJhAkELATIF93cml0ZV9jYWxsYmFja3PdRBmAsBMrFBRnYXR0c19yZWFkJBA2ASYUsBMFJBBVJBQ0AVlCEICwFAhpbmZvIwexEgZoZXixNAE2A1lRYwUAAIkKZXZlbnQIZGF0YXMOd2l0aCBzZXJ2aWNlczpzEUZvdW5kIHBlcmlwaGVyYWw6cw5OZXcgY29ubmVjdGlvbnMMRGlzY29ubmVjdGVkcx1VbmhhbmRsZWQgZXZlbnQsIG5vIHByb2JsZW06IIEUuwEQEmFkdmVydGlzZTAuLi9tcHlfcm9ib3RfdG9vbHMvYnQucHmQUSgAEgB7IwM0AVmwExEUGmdhcF9hZHZlcnRpc2WyEBBhZHZfZGF0YbE2ggFZUWMBAACJDnBheWxvYWQWaW50ZXJ2YWxfdXNzFFN0YXJ0aW5nIGFkdmVydGlzaW5nSCsOEG9uX3dyaXRlDZBVALKwExmxVlFjAAAAiRh2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\n'), '0197a7cfbeef524fd82a75e9df2d3b80d132de0edacdde52f0826975fa75f3e5'), ('light_matrix.mpy', ('TQUCHyCnXDiYBAAHRC4uL21weV9yb2JvdF90b29scy9saWdodF9tYXRyaXgucHk5KFAkJCREIiAoKCgoTCAoKCgoTCAoKCgoTCAoKCgoTCAoKCgoTCAoKCgoTCAoKCgoTCAoKCgoTCAoKCgoTCAoKCgobyAiICsrKytPICsrKytPICsrKytPICsrKytPICsrKytPICsrKytPICsrKytPICsrKytPICsrKytPICsrKytyIIUWhSkAgBAOZGlzcGxheRAKSW1hZ2UqAhsGaHViHAUWARwFFgFZgFEbCnV0aW1lFgGAEBJyYW5kcmFuZ2UqARsMcmFuZG9tHAMWAVmAFgAIiBYCT4YWAniJFgJCLAoRAAgRAAgrAhEACBEACCsCEQAIEQAIKwIRAAgRAAgrAhEACBEACCsCKwWAYhEACBEFKwIRAREBKwIRAAgRASsCEQAIEQErAhEACBEBKwIrBYFiEQERASsCEQAIEQErAhEBEQErAhEBEQAIKwIRAREBKwIrBYJiEQERASsCEQAIEQErAhEBEQErAhEACBEBKwIRAREBKwIrBYNiEQERAAgrAhEBEQAIKwIRAREBKwIRAAgRASsCEQAIEQErAisFhGIRAREBKwIRAREACCsCEQERASsCEQAIEQErAhEBEQErAisFhWIRAREACCsCEQERAAgrAhEBEQErAhEBEQErAhEBEQErAisFhmIRAREBKwIRAAgRASsCEQERAAgrAhEBEQAIKwIRAREACCsCKwWHYhEBEQErAhEBEQErAhEFEQErAhEDEQErAhEBEQErAisFiGIRAREBKwIRAREBKwIRAREBKwIRAAgRASsCEQERASsCKwWJYhYOdGVuc19weCwKEQcRAREBKwMRAREACBEBKwMRAREACBEBKwMRAREACBEBKwMRAREBEQErAysFgGIRAAgRAREACCsDEQERAREACCsDEQAIEQERAAgrAxEACBEBEQAIKwMRAREBEQErAysFgWIRAREBEQErAxEACBEACBEBKwMRAREBEQErAxEBEQAIEQAIKwMRAREBEQErAysFgmIRAREBEQErAxEACBEACBEBKwMRAREBEQErAxEACBEACBEBKwMRAREBEQErAysFg2IRAREACBEBKwMRAREACBEBKwMRAREBEQErAxEACBEACBEBKwMRAAgRAAgRASsDKwWEYhEBEQERASsDEQERAAgRAAgrAxEBEQERASsDEQAIEQAIEQErAxEBEQERASsDKwWFYhEBEQERASsDEQERAAgRAAgrAxEBEQERASsDEQERAAgRASsDEQERAREBKwMrBYZiEQERAREBKwMRAAgRAAgRASsDEQAIEQERAAgrAxEACBEBEQAIKwMRAAgRAREACCsDKwWHYhEBEQERASsDEQERAAgRASsDEQERAREBKwMRAREACBEBKwMRAREBEQErAysFiGIRAREBEQErAxEBEQAIEQErAxEBEQERASsDEQAIEQAIEQErAxEBEQERASsDKwWJYhYQdW5pdHNfcHgyABYQaW1hZ2VfOTkyARYSY29kZWxpbmVzVDICEBZMTUFuaW1hdGlvbjQCFgFRYwADhChdJgUdgJwoI1RmRickRCMmfS4AEhkjATQBwUgZAICwV1vaRgeAIoBj2kICgFpZQwKAsWNKBwBZsWNKAQBdEgBesDQBwLCK+MKwivbDKwDEgEIYgFfFtBIPs1W1VRINslW1VfIrAeXEgeVXhddD4n9ZEAI6FABoMgK0NAE2AcYSB7Y0AWMBAQxudW1iZXJzHTAwMDAwOjA5MDkwOjAwOTAwOjA5MDkwOjAwMDAwgRBRDhQ8bGlzdGNvbXA+DYCuACsAsF9LEwDBEAABFABoMgGxNAE2AS8UQup/YwABAAV0QQ4DA4CuACsAsF9LDADBEgCXsTQBLxRC8X9jAAAABYcQ8EBEEwOAsmBgHydDIiBDJycmQyZtJiYmQyZMSiIjKCwqIwCAgICAgCsFgICAgIArBYCAgICAKwWAgICAgCsFgICAgIArBSsFwLBnWYDBQlWAEhuGNAHCsoBCFoBXw4awsVWzVrBnWYmwsVWzVrBnWYHlWFrXQ+R/WVmyhddEIYCAQhaAV8SJsLFVslawZ1mAsLFVslawZ1mB5VeG10Pkf1mxgeXBsYXXQ6V/gcVCKICwFAB4gDYBWbCAgICAgCsFKwHlwLGA2EQEgLGB5sGwZ1kSAYI0AcW1Q9R/Qm5/UWMAAIE0CBYVBYzbgBSJBwARABcWABYQAxYAGowqAVMzABYAEVEqAVMzARYcdXBkYXRlX2Rpc3BsYXlRYwACgWSrARYAEQWA8CUuLCUAsbAYDGZyYW1lcxIAXiKHaLL3NAGwGBBpbnRlcnZhbBIlFBB0aWNrc19tczYAsBgUc3RhcnRfdGltZYCwGB5uZXh0X2ZyYW1lX3RpbWWAsBgaY3VycmVudF9mcmFtZVFjAAAAiQ0GZnBziFzaAS4TE4D3JDUpH0cwKlEwKlEsNSsxRQCxQxWAEhEUFHRpY2tzX2RpZmYSAxQTNgCwExM2AsGxsBMT20TZgICAgICAKwWAgICAgCsFgICAgIArBYCAgICAKwWAgICAgCsFKwXCEAAZEgBMsBMRNAHdRBuAEgB0sBMBNAHCsFcTA7ATFeVaGANCbYASAGuwEwWAVTQBgthEG4CwEwGwExVVwrBXEwWwEwflWhgDQiGAsBMHsBMHVYFVwrA=\n', 'VxMFsBMFsBMFVYBV5VoYBbBXEwOB5VoYAbATARIAa7ATBTQB20QFgICwGAMSMxQIc2hvdxIlECcUAGgyArI0ATYBNAE2AVlRYwABAIkIdGltZYEQUQ4nHZAKACsAsF9LEwDBEAABFABoMgGxNAE2AS8UQup/YwABAAV0QQ4DA5AKACsAsF9LDADBEgCXsTQBLxRC8X9jAAAABQ==\n'), '840f1af2a2068017d08d8f3315a3eab73db21021a79a571463fb49236e801974'), ('helpers.mpy', ('TQUCHyCCMBAYAAc6Li4vbXB5X3JvYm90X3Rvb2xzL2hlbHBlcnMucHkgUG6LByREAIAQCHBvcnQqARsGaHViHAMWAVki/xwigGQqAlMzARYSY2xhbXBfaW50gCMAKgJTMwIWGHRyYWNrX3RhcmdldIAWDl9fTVNIVUKBFhRfX1BZQlJJQ0tTVDIDEA5QQk1vdG9yNAIWAVFjAQNmAzEuNXizgAEOCQ9gIAASBm1heBIGbWluEgBesDQBsjQCsTQCYwAAAm4KZmxvb3IOY2VpbGluZ4Esw4ABFBUNgAcpJE4AsBQAVjYAgVXDsBQGcHdtEhGzsfOy0fQ0ATYBWbNjAAAKbW90b3IMdGFyZ2V0CGdhaW6CFAgkGQ2MEWBghRRlYGVlYIUOABEAFxYAFhADFgAaMgEWABEyAhYEZGMyAxYSYWJzX2FuZ2xlMgQWCmFuZ2xlMgUWFnJlc2V0X2FuZ2xlIwAqAVMzBhYXUWMBBmYDMS41hHQqKgARDYAYJycrKiglKiglKkgnVUgAEgBMsTQBwiMCst1EFYCxExxfbW90b3Jfd3JhcHBlchMVsBgBEiewGACeQlqAEABWst1ED4CxsBgDEgOwGACeQkOAEBJydW5fYW5nbGWy3UQPgLGwGAUSKbAYAJ5CLIAQAKCy3UQcgBIHsBgAnhIAUBAKcG9ydC6x8hAMLm1vdG9y8jQBsBgJQgiAEgB7IwM0AVmwFBM2AFlRYwIAAIkDcw5fbW90b3Jfd3JhcHBlcnMSVW5rbm93biBtb3RvciB0eXBlghQqFBkTgCwrMysAsBMAnhIN2UQTgLATBxQjEiOxNAE2AVlCGYCwEwCeEhPZRA6AsBMHFA2xNgFZQgCAUWMAAACJCGR1dHlUEQ4fEYAyALATCRQAVjYAglVjAAAAiYF0ERQfBYA1KywrALATAJ4SE9lEDICwEwcUAFY2AIFVY7ATAJ4SD9lEDYCwEwMUCTYAWUIAgFFjAAAAiYN4sYCAQB4VC4A9KyssKCZOMCsAsBMAnhIL2URDgBIAa7E0AYDZRCiAsBMJFABWNgCCVcKyIoE02EQGgLIigmjmwrATARQMcHJlc2V0sjYBWUINgLATAxQDsYBVNgFZQhqAsBMAnhIN2UQPgLATBRQLsVM3AFlCAIBRYwAAAImCDLMBFiENgEkrjwcrALATAJ4SDdlED4ASBbATCbGyNANZQhmAsBMAnhIL2UQOgLATAxQFsTYBWUIAgFFjAAAAiScn\n',), '636b2876d260877dc288b50a257e4a8a4459c7ad43acc8c2fbd671942f16a17a'), ('motor_sync.mpy', ('TQUCHyCDSCAkAAdALi4vbXB5X3JvYm90X3Rvb2xzL21vdG9yX3N5bmMucHkgcGCOUIoJb0CPC4tfAIBRGwhtYXRoFgGAURsKdXRpbWUWAVKBUoAjACoFUzMBFihsaW5lYXJfaW50ZXJwb2xhdGlvboCAKgJTMwIWDGxpbmVhciKAZCKHaIAqA1MzAxYSc2luZV93YXZlIoBkIodogCoDUzMEFhRibG9ja193YXZlVDIFEBBBTUhUaW1lcjQCFgFUMgYQEk1lY2hhbmlzbTQCFgFRYwEGZgMwLjCEIIqVgAGqgIABCxGACIAVjgcoJ2ZrIyRvcoshAAABAgQFCAkKJQAUAI8QAGkyCDaCAFklAIBVgFUnCCUAf1WAVca2JQjzJwmyuCAJAiUANAEnAIAnCrNED4AlAH9VgVUlAIBVgVXzJwoSBm1pbhIGbWF4IwYlBTQCIwc0AicFsLG0tbi5uiAKB8e3YwIDDHBvaW50cxB3cmFwcGluZwpzY2FsZRhhY2N1bXVsYXRpb24WdGltZV9vZmZzZXQSc21vb3RoaW5nZgMwLjBmAzEuMDQRDhA8bGFtYmRhPhOAHQCwgFVjAAAKcG9pbnSBEGMOFDxsaXN0Y29tcD4FgCkAKwCyX0sTADACw8SzJQHzJQC09CoCLxRC6n9jAAAABQAFAAWGbMiQBDQQZnVuY3Rpb24DgDZIRSsnK2clZUAtayooJCkleiM1ALclBCUC8ubHJQFDJIC3JQCAVYBV2kQHgCUAgFWBVWO3JQB/VYBV20QHgCUAf1WBVWO3JQX4yLclBfbJEgBrJQA0AYBCbYBXyrglALpVgFXXRF6AJQC6gfNVMALLzCUAulUwAs3Ovrzzz7i787278/cmECUDRBqAgRIpFAZjb3MSAxMEcGkkEPQ2AfOC9yYRQgOAgCYRvCUDJBH0v/TygSUD8yQQ9L/08iYSuSUG9CQS8mOB5Vha10ONf1lZUWMAAAAFAAUABQAFAAUABQAFAniBCLOAAZQBLQuAWGApRgAABLHRJQD0svInBLC0IAMCw7NjAAEMZmFjdG9yFHRpbWVfZGVsYXkMb2Zmc2V0RCMOEwmAXQCyJQD0JQHyYwAAAAUABQ1ks4EBkQEzBYBhRwAAAQKwsbIgAwPDs2MAARJhbXBsaXR1ZGUMcGVyaW9kDYEYuAQODQmAYgASFxQGc2lusyUC8yUB94L0EgMTGfQ2ASUA9GMAAAAFAAUABRNos4EBkwE5C4BmZ2AAAAECsLGyIAMDw7NjAAETExOBUMAEFBMJgGclOUMAsyUB+MQlArRXW9dGC4AlAiUBgvby10ICgFpZRAOAJQBjJQDRY1FjAAAABQAFAAUKdGlja3OEcAg6OwWMcYATjAiKDG1AZUBlZUBlZWVqQI0IaiAAEQAXFgAWEAMWABoih2iAKgJTMwAWABEREHByb3BlcnR5MgE0ARYIdGltZREBEwxzZXR0ZXIyAjQBFgMyAxYKcGF1c2UyBBYAljIFFgCSMgYWDHJlc3VtZTIHFgpyZXNldDIIFgCDEQsyCTQBFghyYXRlEQETDTIKNAEWAxEFMgs0ARYYYWNjZWxlcmF0aW9uEQETBzIMNAEWA1FjAA2CAKOAARgAEROAhSUlJSkqAFKwGA5ydW5uaW5ngLAYFHBhdXNlX3RpbWVQsBgmcmVzZXRfYXRfbmV4dF9zdGFydLEih2j3sBgcX19zcGVlZF9mYWN0b3KyIr2EQPewGBxfX2FjY2VsX2ZhY3RvchIKdXRpbWUUEHRpY2tzX21zNgCwGBRzdGFydF90aW1lUWMAAACJGRWCMCkaIReAjic1IygnaACwExdEL4ASDxQUdGlja3NfZGlmZhIDFBE2ALATETYCwRIAXrATE7GC+fSwExWx9PKwExnyNAFjsBMBY1FjAAAAiXQaEBMTgJolALGwGAUSDxQPNgCwGA9RYwAAAIkOc2V0dGluZ4EEERIlDYCeJygAsBMXRA2AsBMRsBgRULAYBVFjAAAAiUgRDgCWB4CjALAUCTYAWVFjAAAAiYEUERIAkgOApicsALATBUMRgBIRFBE2ALAYEVKwGAdRYwAAAIlIEQ4lC4CrALAUAJI2AFlRYwAAAIlAEQ4lA4CuAICwGBNRYwAAAIlYGQ4AgwOAsQCwVxMff+daGAFRYwAAAImBPCkQAQOAtTUAEhEUHRIDFBM2ALATEzYCwbATHbH0sBMd8iKHaPRjAAAAiYFoIhYPD4C6LScnKQCwEwWxIodo99xEHoCwExdEB4CwFBk2AFmxIodo97AYBbAUAJI2AFlRYwAAAIkdTBEOHwuAwgCwEw8ivYRA9GMAAACJgiQiGAUFgMYuJycsKgCwEwWxIr2EQPfcRCuAsBMNRAeAsBQNNgBZsBMPIodo97AYD7EivYRA97AYCbAUAJI2AFlRYwAAAIkPgmwQJhJNZWNoYW5pc20PjNCAGI4JigtqYIUQjB4AEQAXFgAWEAMWABpSIoBkIwAqA1MzARYAESsAKgFTMwIWLnJlbGF0aXZlX3Bvc2l0aW9uX3Jlc2V0EQCUMgM0ARYmZmxvYXRfdG9fbW90b3Jwb3dlcjIEFiJ1cGRhdGVfbW90b3JfcHdtc4CUKwAqA1MzBRYmc2hvcnRlc3RfcGF0aF9yZXNldDIGFgCWUWMBBmYDMS4ygVS6hQEYABELgOopJSUlJAAyBrE0AbAYDG1vdG9yc7KwGB5tb3Q=\n', 'b3JfZnVuY3Rpb25ztLAYEHJhbXBfcHdttbAYBEtws0QHgLAUETYAWVFjAAEAiQkJFHJlc2V0X3plcm8LC4E8SQ4UPGxpc3Rjb21wPg+A6gArALBfSx4AwRAcX21vdG9yX3dyYXBwZXISAEyxNAHdRAqAsRMBEwptb3RvckIBgLEvFELff2MAAAAFgnTaARwTB4DyJE4yJCkoJgCxQw6AgSsBEgBrsBMTNAH0wRIApbATAbE0Al9LKgAwAsLDs0QfgLIUAFY2AIJVxLQigTTYRAaAtCKCaObEshQMcHJlc2V0tDYBWULTf1FjAAAAiR5tb3RvcnNfdG9fcmVzZXSBACEOHQmQAAASBm1pbhIGbWF4EgBesDQBIv8cNAIigGQ0AmMAAAJmhDCKkMBAICMJkAQ1JykvSzEmTEgAEgClsBMRsBMhNAJfS2QAMALExbWxsrM1Aca0FABWNgCBVcewFA+2t/OwEx30NgHIsBMfIoBk10QrgBIAXrATARIAObE0AfQ0Acm4gNdEDIASEbi50TQCyEIIgBITuLk0Asi0FAZwd224NgFZQpl/UWMAAACJCnRpY2tzhlCIlQEwJxWQFCRuaDckKkkqLCpMbEsgIykwALNDDoCBKwESAGuwExU0AfTDsBQfszYBWRIApbATA7ATF7M0A19LVAAwA8TFxrZESIASAF61sTQBNAHHtBQAVjYAgVXIt7jzIoE02EQMgLQUH7gigmjyNgFZt7jzIv5M10QMgLQUAbgigmjzNgFZtBQecnVuX3RvX3Bvc2l0aW9ut7I2AllCqX8SPxQQc2xlZXBfbXMiMjYBWSsAybATC19LEQDEubQUAFY2AINVKwHlyULsfxIAO7k0AUMDgEIDgELVf1FjAAAAiRMKc3BlZWQngQBBEACWFZAxKQCwEwlfSwwAwbEUGYA2AVlC8X9RYwAAAIk=\n'), 'ff07c3fee21207cebf5f313c0b261fe5352db2569387c656aaa956accad9fa63'))

def calc_hash(b):
    return hexlify(uhashlib.sha256(b).digest()).decode()

error=False
try:
    os.mkdir('/projects/mpy_robot_tools')
except:
    pass

for file, code, hash_gen in encoded:
    print("Writing file ", file)
    # hash_gen=code[1]
    target_loc = '/projects/mpy_robot_tools/'+file
    
    print('writing '+file+' to folder /projects/mpy_robot_tools')
    with open(target_loc,'wb') as f:
        for chunk in code:
            f.write(ubinascii.a2b_base64(chunk))

    print('Finished writing '+file+', Checking hash.')
    result=open(target_loc,'rb').read()
    hash_check=calc_hash(result)

    print('Hash generated: ',hash_gen)

    if hash_check != hash_gen:
        print('Failed hash of .mpy on SPIKE: '+hash_check)
        error=True

if not error:
    print('Library written succesfully. Resetting....')
    machine.reset()
else:
    print('Failure in writing library!')