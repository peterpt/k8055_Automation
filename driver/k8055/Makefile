# $Id: Makefile,v 1.5 2008/05/21 20:22:44 mr_brain Exp $
#
# Modernized Makefile for the libk8055 library (v0.4.2)
# Adapted for libusb-1.0 and modern GCC.
#

# --- Configuration ---
# Installation prefix. Default is /usr/local
PREFIX = /usr/local
CC = gcc
EXEC = k8055
VERSION = 0.4.2 

# --- Paths ---
BINDIR = $(PREFIX)/bin
LIBDIR = $(PREFIX)/lib
INCLUDEDIR = $(PREFIX)/include
MANDIR = $(PREFIX)/man/man1
PYLIBDIR = pyk8055
GUIDIR = gui

# --- Object files for the command-line program ---
OBJS = main.o libk8055.o

# --- Modern Flags ---
# Use pkg-config to get the correct compiler and linker flags for libusb-1.0
# This is the key change that replaces the hardcoded "-lusb".
USB_CFLAGS = $(shell pkg-config --cflags libusb-1.0)
USB_LIBS   = $(shell pkg-config --libs libusb-1.0)

# CFLAGS for compiling all C source files.
# -fPIC is required to create position-independent code for the shared library.
CFLAGS = -O2 -Wall -g -fPIC -DDAEMON -DVERSION='"$(VERSION)"' $(USB_CFLAGS)

# LIBS for linking. Includes modern libusb and the math library.
LIBS = $(USB_LIBS) -lm

# --- Build Targets ---

# Default target: build the command-line program, shared library, and static library.
all: k8055_prog libk8055.so libk8055.a

# Rule to build the shared library (e.g., libk8055.so.0.4.2)
libk8055.so: libk8055.so.$(VERSION)
	@echo "--> Linking shared library symlink: libk8055.so -> $<"
	@ln -sf $< $@

libk8055.so.$(VERSION): libk8055.o
	@echo "--> Linking shared library: $@"
	$(CC) -shared -o $@ $^ $(LIBS)

# Rule to build the static library (e.g., libk8055.a)
libk8055.a: libk8055.o
	@echo "--> Creating static library: $@"
	ar rvs $@ $^

# Rule to build the main executable program
k8055_prog: $(OBJS)
	@echo "--> Linking executable: $(EXEC)"
	$(CC) -o $(EXEC) $(OBJS) $(LIBS)

# Generic rule to compile .c files into .o object files
%.o: %.c k8055.h
	@echo "--> Compiling: $<"
	$(CC) $(CFLAGS) -c $< -o $@

# --- Sub-project Targets ---

pylib: libk8055.so
	@echo "--> Building Python sub-project..."
	@export VERSION=$(VERSION); $(MAKE) -C $(PYLIBDIR)

k8055gui: libk8055.so
	@echo "--> Building GUI sub-project..."
	@$(MAKE) -C $(GUIDIR)

# --- Management Targets ---

clean:
	@echo "--> Cleaning project..."
	@rm -f *.o libk8055.so libk8055.so.* $(EXEC) libk8055.a
	#@$(MAKE) -C $(PYLIBDIR) clean
	@$(MAKE) -C $(GUIDIR) clean

install: all
	@echo "--> Installing files to $(PREFIX)..."
	@mkdir -p $(BINDIR) $(LIBDIR) $(INCLUDEDIR) $(MANDIR)
	cp -f $(EXEC) $(BINDIR)/
	cp -Pf libk8055.so* $(LIBDIR)/
	cp -f libk8055.a $(LIBDIR)/
	cp -f k8055.h $(INCLUDEDIR)/
	cp -f man/k8055.1.gz $(MANDIR)/
	@echo "--> Installation complete."

pyinstall: pylib
	@echo "--> Installing Python module..."
	@$(MAKE) -C $(PYLIBDIR) install

guiinstall: k8055gui
	@echo "--> Installing GUI application..."
	@$(MAKE) -C $(GUIDIR) install

uninstall:
	@echo "--> Uninstalling files from $(PREFIX)..."
	rm -f $(BINDIR)/$(EXEC)
	rm -f $(LIBDIR)/libk8055.so* $(LIBDIR)/libk8055.a
	rm -f $(INCLUDEDIR)/k8055.h
	rm -f $(MANDIR)/k8055.1.gz
	@echo "--> Uninstallation complete."

test: k8055_prog
	-@killall $(EXEC)
	./$(EXEC)

# Mark targets that are not files
.PHONY: all pylib k8055gui clean install pyinstall guiinstall uninstall test
