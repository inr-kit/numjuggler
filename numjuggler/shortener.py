
def f(l):

    iR = 0
    iD = 0
    iI = 0
    es = l[0]
    for e in l[1]:
        if iR > 0:
            # r-series is active.
            if e == es:
                # continue r-series
                iR += 1
            else:
                # r-series stops here.
                yield es
                yield '{}r'.format(iR)
                iR = 0
                es = e
        elif iD != 0:
            # i-resies is active. iD is the difference, and ep -- previous element
            if e - ep == iD:
                # i-series continues
                iI += 1
                ep = e
            else:
                # i-series stops here.
                yield es
                yield '{}i'.format(iI)
                yield ep
                iI = 0
                iD = 0
                es = e
        else:
            # there is no active series, and es -- previous element.
            if e == es:
                # r-series starts here
                iR = 1
            else:
                # i-series starts here
                iI = 0
                iD = e - es

if __name__ == '__main__':
    pass



