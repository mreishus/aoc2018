defmodule Elixir2016.Day23 do
  alias Elixir2016.Day23.BunnyVM

  def part1(filename) do
    vm =
      parse(filename)
      |> BunnyVM.new()
      |> BunnyVM.register_set("a", 7)
      |> BunnyVM.execute()

    vm.registers
  end

  def part2(filename) do
  end

  def parse(filename) do
    File.stream!(filename)
    |> Stream.map(&String.trim/1)
    |> Stream.map(&String.split/1)
    |> Enum.map(fn list ->
      list |> Enum.map(&try_parse_int/1)
    end)
  end

  def try_parse_int(string) do
    case Integer.parse(string) do
      :error -> string
      {num, _} -> num
    end
  end
end

defmodule Elixir2016.Day23.BunnyVM do
  alias Elixir2016.Day23.BunnyVM

  defstruct [
    :memory,
    :pc,
    :registers,
    :toggled
  ]

  def init_registers() do
    Enum.to_list(?a..?d)
    |> List.to_string()
    |> String.graphemes()
    |> Map.new(fn letter -> {letter, 0} end)
  end

  def new(memory) do
    memory_map =
      memory
      |> Enum.with_index()
      |> Enum.map(fn {line, i} -> {i, line} end)
      |> Enum.into(%{})

    %BunnyVM{
      memory: memory_map,
      pc: 0,
      registers: init_registers(),
      toggled: false
    }
  end

  def register_set(vm, reg, value) do
    registers = Map.put(vm.registers, reg, value)
    %{vm | registers: registers}
  end

  def lookup(_, arg) when is_integer(arg), do: arg

  def lookup(vm, arg) when is_binary(arg) do
    vm.registers |> Map.get(arg)
  end

  def execute(%BunnyVM{memory: memory, pc: pc} = vm) do
    instruction = memory |> Map.get(pc)

    if instruction != nil do
      %{pc: pc, i: instruction} |> IO.inspect()
      # %{pc: pc, i: instruction, registers: vm.registers} |> IO.inspect()

      do_execute_step(vm, instruction)
      |> execute()
    else
      vm
    end
  end

  # # Optimization: pc 4 always jumps to pc 9
  # def do_execute_step(%{pc: 4} = vm, _) do
  #   %{vm | pc: 9}
  # end

  # # Optimization: pc 10-12: Sets a += b, b = 0, then moves to 13
  # def do_execute_step(%{pc: 10} = vm, _inst) do
  #   a = Map.get(vm.registers, "a")
  #   b = Map.get(vm.registers, "b")

  #   registers =
  #     vm.registers
  #     |> Map.put("a", a + b)
  #     |> Map.put("b", 0)

  #   %{vm | registers: registers, pc: 12}
  # end

  # # Optimization: pc 18-20: Sets a += d, d = 0, then moves to 21
  # def do_execute_step(%{pc: 18} = vm, _) do
  #   a = Map.get(vm.registers, "a")
  #   d = Map.get(vm.registers, "d")

  #   registers =
  #     vm.registers
  #     |> Map.put("a", a + d)
  #     |> Map.put("d", 0)

  #   %{vm | registers: registers, pc: 20}
  # end

  def do_execute_step(vm, ["cpy", arg1, arg2]) do
    registers = Map.put(vm.registers, arg2, lookup(vm, arg1))
    %{vm | registers: registers, pc: vm.pc + 1}
  end

  def do_execute_step(vm, ["inc", arg1]) do
    registers = Map.update!(vm.registers, arg1, fn x -> x + 1 end)
    %{vm | registers: registers, pc: vm.pc + 1}
  end

  def do_execute_step(vm, ["dec", arg1]) do
    registers = Map.update!(vm.registers, arg1, fn x -> x - 1 end)
    %{vm | registers: registers, pc: vm.pc + 1}
  end

  def do_execute_step(vm, ["jnz", arg1, arg2]) do
    arg1 = lookup(vm, arg1)
    arg2 = lookup(vm, arg2)

    if arg1 != 0 do
      %{vm | pc: vm.pc + arg2}
    else
      %{vm | pc: vm.pc + 1}
    end
  end

  def do_execute_step(vm, ["tgl", arg1]) do
    arg1 = lookup(vm, arg1)
    toggle_idx = vm.pc + arg1

    if Map.has_key?(vm.memory, toggle_idx) do
      "Toggling index #{toggle_idx}" |> IO.inspect()
      memory = Map.update!(vm.memory, toggle_idx, &toggle_instruction/1)
      %{vm | memory: memory, pc: vm.pc + 1}
    else
      %{vm | pc: vm.pc + 1}
    end
  end

  def toggle_instruction([inst, a, b]) do
    [toggle_instruction(inst), a, b]
  end

  def toggle_instruction([inst, a]) do
    [toggle_instruction(inst), a]
  end

  def toggle_instruction(inst) do
    # For one-argument instructions, inc becomes dec, and all other one-argument instructions become inc.
    # For two-argument instructions, jnz becomes cpy, and all other two-instructions become jnz.
    case inst do
      ## One
      "inc" -> "dec"
      "dec" -> "inc"
      "tgl" -> "inc"
      ## Two
      "cpy" -> "jnz"
      "jnz" -> "cpy"
    end
  end
end
