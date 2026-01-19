function read_bpplib_instance(path)
    data = readlines(path)
    # First line contains n
    n = parse(Int, data[1])
    # Second line contains capacity
    c = parse(Int, data[2])

    # Collect all remaining numbers, on the n following lines
    weights = []
    for line in data[3:end]
        append!(weights, parse.(Int, split(line)))
    end

    if length(weights) != n
        error("Error: expected $n weights but got $(length(weights))")
    end

    return n, c, weights
end
