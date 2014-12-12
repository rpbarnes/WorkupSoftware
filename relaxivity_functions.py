from matlablike import *
Dw_default = 2.3e-9 # Brandon's
Dsl_default = 4.1e-10 # Brandon's
d_default = 0.47e-9 # hodges + bryant, surface label for bilayer at 298K
d_free = 0.3e-9 # just what I need to give me what I want for tau
d_buried = 0.8e-9 # this is made up
tau_rot_default = 5e-9
default_normalization_ratio = normalization_ratio = 2e26 # the hand-picked weighting between the rotational and the translational

def tau(Dw = Dw_default, Dsl = Dsl_default, d = d_default,tau_rot = 'junk',normalization_ratio = 'junk'):
    return d**2/(Dw+Dsl)
def J_ffhs(f,**kwargs):
    z = sqrt(1j*2*pi*f*tau(**kwargs))
    return c_prime(**kwargs)*real((1.+z/4.)/(1.+z+4./9.*z**2+1./9.*z**3))
#def J(f,**kwargs):
#    return J_ffhs(f,**kwargs)
def ksigma(f,**kwargs):
    fH = 1.51671e-3*f
    return 6*J(f-fH,**kwargs)-J(f+fH,**kwargs)
def krho(f,**kwargs):
    fH = 1.51671e-3*f
    return 6*J(f-fH,**kwargs)+3*J(fH,**kwargs)+J(f+fH,**kwargs)
def klow(f,**kwargs):
    return 5./3.*krho(f,**kwargs)-7./3.*ksigma(f,**kwargs)
def c_prime(Dw = Dw_default, Dsl = Dsl_default, d = d_default,tau_rot = 'junk',normalization_ratio = 'junk'):
    # this is bennati's k', which is multiplied by 7J(omega_s,tau_D)+3J(omega_I,tau_D) to get the diffusion
    #kprime = 32000.*pi/405.(mu_0/4./pi)**2*N_A*C*(gamma_H*g_e*mu_B)**2*S*(S+1)/(d*(D_M+D_L))
    # remember that hbar*omega/B_0 = g*mu_B = gamma_e*hbar, so 
    # also, eliminate C, so that this gives a relaxivity, rather than a relaxation rate
    gamma_e = gamma_H/1.51671e-3
    S = 0.5
    kprime = 32000.*pi/405
    kprime *= (mu_0/4./pi)**2
    kprime *= N_A
    kprime *= (hbar*2*pi*gamma_H*2*pi*gamma_e)**2 # here, I am converting from my usual circular units to angular units
    kprime *= S*(S+1)
    kprime /= d*(Dsl+Dw)
    #print 'for: <d> ={}\Ang <D>={}'.format(d.mean()/1e-10,Dsl+Dw.mean()),
    #print 'kprime is {}--{}'.format(kprime.min(),kprime.max())
    return kprime
def J_rot(f,tau_rot = tau_rot_default,**extrakwargs):
    return real(tau_rot/(1+2j*pi*f*tau_rot))
def J(f,rot_weighting = 0.5,normalization_ratio = default_normalization_ratio,**kwargs):
    if rot_weighting != 0:
        J_ffhs_at_zero = J_ffhs(0,**kwargs)
        J_rot_at_zero = J_rot(0,**kwargs)
        return (1.0-rot_weighting)*J_ffhs(f,**kwargs)+rot_weighting*J_rot(f,**kwargs)*normalization_ratio
    else:
        #print "yes, rot weighting is 0:"
        return J_ffhs(f,**kwargs)

