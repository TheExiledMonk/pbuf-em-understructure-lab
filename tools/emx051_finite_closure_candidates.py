from __future__ import annotations
import hashlib, numpy as np
from emx049_new_reference_geometry_primitive import DIRECTIONS, DT, N, NORM, STEPS, source

def sha(a): return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def shift(a,d): return np.roll(a,d,axis=(0,1,2))
def lap(u): return sum(shift(u,d)-u for d in DIRECTIONS)
def norm(a):
 n=np.sqrt(np.sum(a*a)); return a*(NORM/n) if n else a
def source_witness(u, candidate):
 if candidate=='GEOMETRY_DIRECTED_WORK':
  g=sum(np.sum((shift(u,d)-u)*np.asarray(d),axis=-1)[...,None]*np.asarray(d) for d in DIRECTIONS)
 else: g=lap(u)
 return norm(g)*0.001
def force(u,candidate): return lap(u)-(0.25*u if candidate=='SYMPLECTIC_PAIRED_STATE' else 0.)
def energy(u,p,candidate): return float(.5*np.sum(p*p)+.25*sum(np.sum((shift(u,d)-u)**2) for d in DIRECTIONS)+(.125*np.sum(u*u) if candidate=='SYMPLECTIC_PAIRED_STATE' else 0.))
def evolve(u,p,w,candidate,dt=DT,steps=STEPS):
 vals=[];ener=[];receiver=[]
 for t in range(steps+1):
  vals.append(float(np.sqrt(np.sum(u*u+p*p))));ener.append(energy(u,p,candidate));receiver.append(float(np.linalg.norm(u[(N//2+3)%N,N//2,N//2])))
  if t==steps:break
  f=force(u,candidate)+w[t];p=p+.5*dt*f;u=u+dt*p;f=force(u,candidate)+w[t+1];p=p+.5*dt*f
 a=np.array(vals);return np.array([a[0],a[-1],a.min(),a.max()]),np.array(ener),np.array(receiver),u,p
def witness_history(u,candidate,enabled=True,steps=STEPS):
 w=np.zeros((steps+1,N,N,N,3));
 if enabled:w[0]=source_witness(u,candidate)
 return w
