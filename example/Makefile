default: example.nes

clean:
	rm -rf .b/

C_SRC = fill_nametable.c \
        create_text.c \
        main.c

S_SRC = crt0.s

C_OBJ = $(patsubst %.c,.b/%.o,$(C_SRC))

S_OBJ = $(patsubst %.s,.b/%.o,$(S_SRC))

.b/%.o: %.c
	mkdir -p .b/
	python ../annotatecc65.py -Oi $< -o $(patsubst %.o,%.s,$@)
	ca65 -o $@ $(patsubst %.o,%.s,$@)

.b/%.o: %.s
	mkdir -p .b/
	ca65 $< -o $@

example.nes: $(C_OBJ) $(S_OBJ)
	python ../annotateld65.py -o example.nes -C nrom.cfg \
    $(C_OBJ) $(S_OBJ) runtime.lib
