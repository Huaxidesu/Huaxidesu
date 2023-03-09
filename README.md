[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Ma+Shan+Zheng&pause=1000&color=00D30C&width=435&lines=%E8%BF%99%E6%98%AF%E4%B8%80%E4%BD%8D%E8%BF%87%E6%B0%94%E7%9A%84%E8%80%81%E8%BD%A6%E8%BD%A6~;%E5%88%AB%E7%9C%8B%E5%95%A6%EF%BC%8C%E5%90%8E%E9%9D%A2%E4%BB%80%E4%B9%88%E9%83%BD%E6%B2%A1%E6%9C%89%E4%BA%86XD)](https://git.io/typing-svg)
[![Anurag's GitHub stats](https://github-readme-stats.vercel.app/api?username=Huaxidesu&count_private=true&show_icons=true&theme=great-gatsby)](https://github.com/anuraghazra/github-readme-stats)
![](https://snakegithub.pages.dev/github-contribution-grid-snake.svg)

- uses: Platane/snk@v2
  with:
    # github user name to read the contribution graph from (**required**)
    # using action context var `github.repository_owner` or specified user
    github_user_name: ${{ github.repository_owner }}

    # list of files to generate.
    # one file per line. Each output can be customized with options as query string.
    #
    #  supported options:
    #  - palette:     A preset of color, one of [github, github-dark, github-light]
    #  - color_snake: Color of the snake
    #  - color_dots:  Coma separated list of dots color.
    #                 The first one is 0 contribution, then it goes from the low contribution to the highest.
    #                 Exactly 5 colors are expected.
    outputs: |
      dist/github-snake.svg
      dist/github-snake-dark.svg?palette=github-dark
      dist/ocean.gif?color_snake=orange&color_dots=#bfd6f6,#8dbdff,#64a1f4,#4b91f1,#3c7dd9
