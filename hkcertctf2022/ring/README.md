# Ring

> Ring ring ring ring ring ring ring banana phone
> - @ozetta

## Question

This is the entirety of `Ring.R`:

    Ring <- function(p){
      tryCatch(
      expr = {
        x <- 1:17
        y <- utf8ToInt(p)
        z <- lm(y ~ poly(x,16))
        u <- as.numeric(summary(z)$coefficients[,1])
        v <- c(94.8823529411764923, -8.0697024752598967, -8.6432639293214333, 
                3.8067684547541667, -2.6157531995857521, 39.7193457764808500, 14.9176635631982180, 
               14.3308668599120725, 43.6042210530751291, 37.5259918448356302, 
                4.0314998333763086,  5.1052914400636569,  1.8689828029874489, 13.7270919105349307, 
               12.8538529135203099,  7.1197700159123247, 10.2656771598556720)
        if(identical(u, v)){
          print(sprintf("hkcert22{%s}", sprintf(p, "ReveRseengineeRing")))
        }else{
          stop()
        }
      },
      error = function(e){
        print("Wrong Password")
      },
      warning = function(w){
        print("Wrong Password")
      })
    }
    Ring(readline(prompt="Enter Password: "))

So, we basically have to reverse-engineer a set of 17 characters in the
printable ASCII range, so that when running a LM upon, we would get the
given coefficient `v`.

## Solution

Literally just two weeks ago, I learned from a stats course about
`optim` and `optimize` functions in R, which sounds like the perfect
approach.

We used the [SSE](https://en.wikipedia.org/wiki/Residual_sum_of_squares)
to measure how close our answer is to the flag.

For initial values, we chose 85, because it is a midpoint between 48
(`0`) and 122 (`z`), which we had confidence that most of the letters
of the flag are nearby.

Let’s give it a quick shot:

    fn <- function (y) {
      x <- 1:17
      z <- lm(y ~ poly(x,16))
      u <- as.numeric(summary(z)$coefficients[,1])
      v <- c(94.8823529411764923, -8.0697024752598967, -8.6432639293214333, 
             3.8067684547541667, -2.6157531995857521, 39.7193457764808500, 14.9176635631982180, 
             14.3308668599120725, 43.6042210530751291, 37.5259918448356302, 
             4.0314998333763086,  5.1052914400636569,  1.8689828029874489, 13.7270919105349307, 
             12.8538529135203099,  7.1197700159123247, 10.2656771598556720)
      sum((u-v) ** 2) # sum of squared residuals
    }

    optim_fn <- function (init) {
      res <- optim(init, fn, control = c(maxit = 10000, abstol = 0.1))
      res$par
    }

    score_par <- function (par) {
      print(par)
      print(fn(par))
      print(intToUtf8(round(par)))
    }

    par1 <- optim_fn(rep(c(85), 17))
    score_par(par1)

    ##  [1]  71.68368  91.77545  92.23233 102.35212  90.27752  73.06679  72.89915
    ##  [8]  73.16237  93.90105 100.19573  99.50889  66.18560  90.95063  86.79578
    ## [15] 100.30925  27.32032 105.13762
    ## [1] 112.2374
    ## [1] "H\\\\fZIII^ddB[Wd\033i"

Looks promising, but not close enough. So let’s re-run it with rounded
values, since we know the source strings are represented in integers
anyways.

    par2 <- optim_fn(round(par1))
    score_par(par2)

    ##  [1]  72.46066  90.90951  93.64148 104.70957  91.86149  73.11547  73.86583
    ##  [8]  73.71544  95.97582 101.87416 100.18324  67.91978  90.89138  87.62399
    ## [15] 100.31563  27.51488 105.66941
    ## [1] 91.34793
    ## [1] "H[^i\\IJJ`fdD[Xd\034j"

    par3 <- optim_fn(round(par2))
    score_par(par3)

    ##  [1]  74.26857  92.78221  94.65882 105.71238  93.17828  75.34449  75.51057
    ##  [8]  74.27791  97.75777 102.71853 102.12162  69.75753  93.20973  89.50195
    ## [15] 101.77483  30.42933 109.03386
    ## [1] 66.87216
    ## [1] "J]_j]KLJbgfF]Zf\036m"

    par4 <- optim_fn(round(par3))
    score_par(par4)

    ##  [1]  75.45662  94.33093  96.41318 107.50440  94.31281  76.47782  75.61402
    ##  [8]  76.06559  97.78344 104.37395 103.55095  69.89687  94.43929  90.14634
    ## [15] 103.34615  30.37030 107.97544
    ## [1] 46.94176
    ## [1] "K^`l^LLLbhhF^Zg\036l"

    par5 <- optim_fn(round(par4))
    score_par(par5)

    ##  [1]  76.79746  95.49097  97.68069 107.71652  95.51062  76.97062  77.17542
    ##  [8]  77.32795  99.44713 105.73930 103.70981  71.35446  95.03586  91.55832
    ## [15] 104.84895  31.40486 109.56654
    ## [1] 33.60124
    ## [1] "M_bl`MMMcjhG_\\i\037n"

At this point here a few iterations down the road, we also tried to
impose a penalty to encourage the optimizer to give us values closer to
integer values.

    fn_penalized <- function (y) {
      x <- 1:17
      z <- lm(y ~ poly(x,16))
      u <- as.numeric(summary(z)$coefficients[,1])
      v <- c(94.8823529411764923, -8.0697024752598967, -8.6432639293214333, 
             3.8067684547541667, -2.6157531995857521, 39.7193457764808500, 14.9176635631982180, 
             14.3308668599120725, 43.6042210530751291, 37.5259918448356302, 
             4.0314998333763086,  5.1052914400636569,  1.8689828029874489, 13.7270919105349307, 
             12.8538529135203099,  7.1197700159123247, 10.2656771598556720)
      sum((u-v) ** 2) + (sum((y - round(y) ** 2)) * 1e2)
    }

    optim_fn_penalized <- function (init) {
      res <- optim(init, fn_penalized, control = c(maxit = 10000, abstol = 0.1))
      res$par
    }

Also, from the original question, we believed that there should be a
`%s` somewhere in the string that we are finding. Since `%` is 37 and
`s` is 115, it is most probable for those to be the 16th and 17th
characters.

Let’s try again.

    round_with_fixed_suffix <- function (par) {
      par[16] <- 37  # `%`
      par[17] <- 115 # `s`
      round(par)
    }
    par6 <- optim_fn_penalized(round_with_fixed_suffix(par5))
    score_par(par6) # the score pumped because we are scoring with `fn`

    ##  [1]  77.0  95.0  98.0 119.5  96.0  77.0  77.0  77.0  99.0 106.0 104.0  71.0
    ## [13]  95.0  92.0 105.0  37.0 115.0
    ## [1] 177.2465
    ## [1] "M_bx`MMMcjhG_\\i%s"

We also tried alternating between the penalized function and the
unpenalized functions to hopefully finding a value that converges
towards the flag.

    par7 <- optim_fn(round_with_fixed_suffix(par6))
    score_par(par7)

    ##  [1]  80.59620  99.14117 101.51997 112.40060  99.68532  81.17027  81.49027
    ##  [8]  81.45603 103.44908 109.63417 108.56694  75.21759  99.54827  95.23295
    ## [15] 108.74539  35.32712 112.94134
    ## [1] 3.262093
    ## [1] "QcfpdQQQgnmKd_m#q"

    par8 <- optim_fn_penalized(round_with_fixed_suffix(par7))
    score_par(par8)

    ##  [1]  81.0  99.0 102.0 123.5 100.0  81.0  81.0  81.0 103.0 110.0 109.0  75.0
    ## [13] 100.0  95.0 109.0  37.0 115.0
    ## [1] 117.9282
    ## [1] "Qcf|dQQQgnmKd_m%s"

This looks super promising, since there is a `%s` at the end after running
it. Let’s try to optimize with `fn` once more:

    par9 <- optim_fn(round_with_fixed_suffix(par8))
    score_par(par9)

    ##  [1]  82.24795 101.25232 103.13155 114.31636 101.13520  83.15467  83.14711
    ##  [8]  83.08179 105.15569 111.23344 110.07631  77.17922 101.20406  97.14304
    ## [15] 110.19022  37.25024 115.13106
    ## [1] 0.09946189
    ## [1] "RegreSSSionMean%s"

Aha! Just to confirm:

    score_par(round(par9))

    ##  [1]  82 101 103 114 101  83  83  83 105 111 110  77 101  97 110  37 115
    ## [1] 1.488095e-19
    ## [1] "RegreSSSionMean%s"

The numbers are not being completely aligned, but we knew we found our
jackpot. Let's try the flag out:

    p <- 'RegreSSSionMean%s'
    sprintf("hkcert22{%s}", sprintf(p, "ReveRseengineeRing"))

    ## [1] "hkcert22{RegreSSSionMeanReveRseengineeRing}"

Yay!

Gotta love the upcoming stats courses a bit more. But before that, back
to my weekly lab assignments (ergh).
