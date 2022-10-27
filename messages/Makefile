# brew install protobuf  (this command will install protoc, allowing you to compile the protobuf files)
protobuf: target.proto
	protoc -I=./ --python_out=./ ./target.proto