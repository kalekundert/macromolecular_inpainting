- How is `BlocksBasisExpansion` different than others?

- Where is `R3Conf.filter` defined?

  - At end of constructor: `self.register_buffer("filter", ...)`
  - It's just a zero vector at this point, but it's the right size.
  -
