OTools --- A framework for online systems
================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

OTools stands for Online Tools, which is a Python/Cython framework for developing
multithread online systems.

This framework provides a simple way to deploy online systems by providing some
concepts of multithread systems such as program scopes, shared memory, locks and
threads in a more understandable and easier to implement way.

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

OTools 101
-----------------

There are basically 7 classes you need to understand in order to use the framework
at its full potential: :mod:`Logger`, :mod:`Context`, :mod:`Dataframe`, :mod:`Service`, :mod:`Trigger`,
:mod:`OTools` and :mod:`Watchdog`.

While explaining each one of them, we'll build and run a SimpleExample_. 

.. _SimpleExample: https://github.com/gabriel-milan/otools/blob/master/examples/simple_example/


.. module:: Logger
   :synopsis: Logger is the main class for getting information about the running system.

:mod:`Logger`
~~~~~~~~~~~~~

The :mod:`Logger` is the messaging core. It provides complete logging by showing from which
context and module it has been called, making it easy to debug code.

You don't really need to worry constructing this module as the framework will handle it for
you, all you have to understand here are the levels of logging.

It has 6 levels of logging, which were parsed into a class, in order to ease the use of it:

.. module:: LoggingLevel
   :synopsis: Logger level wrapper

.. attribute:: VERBOSE

   * **Color**: white
   * **Shows**: *VERBOSE*, *DEBUG*, *INFO*, *WARNING*, *ERROR* and *FATAL*

.. attribute:: DEBUG

   * **Color**: cyan
   * **Shows**: *DEBUG*, *INFO*, *WARNING*, *ERROR* and *FATAL*

.. attribute:: INFO

   * **Color**: green
   * **Shows**: *INFO*, *WARNING*, *ERROR* and *FATAL*

.. attribute:: WARNING

   * **Color**: bold yellow
   * **Shows**: *WARNING*, *ERROR* and *FATAL*

.. attribute:: ERROR

   * **Color**: red
   * **Shows**: *ERROR* and *FATAL*
   * **Raises**: tries to raise any identified error on execution. If none found, doesn't raise anything.

.. attribute:: FATAL

   * **Color**: bold red
   * **Shows**: *FATAL* only
   * **Raises**: tries to raise any identified error on execution. If none found, raise FatalError.


.. module:: Context
   :synopsis: Context is an object that allows communication between modules attached to OTools

:mod:`Context`
~~~~~~~~~~~~~~

The :mod:`Context` is the core of communication between the modules of the framework. Objects
of type :mod:`Service`, :mod:`Dataframe` and :mod:`Trigger` can be attached to it, and so it
allows you to access them from your own running :mod:`Service` without worrying too much.

Your system can orchestrate one or many :mod:`Context` objects, some of them sharing :mod:`Dataframe`
objects or whatever, it's up to your imagination.

The most important methods you need to know in order to make it work are the following:

.. function:: __init__ (level = LoggingLevel.INFO, name = "Unnamed")
   
   The constructor sets as default *INFO* as the logging level and *Unnamed* as the name of the
   context. Notice that there might not be two :mod:`Context` objects with the same name running on the
   same instance of :mod:`OTools`.

.. function:: __add__ (obj)
   
   You can add only :mod:`Service`, :mod:`Dataframe` and :mod:`Trigger` objects to the context.
   Each of them will have different handling, but be aware that :mod:`Trigger` and :mod:`Service`
   objects can't have the same name on the same context. :mod:`Dataframe` objects also can't have
   the same name on same context.

Beginning our SimpleExample_, we now construct the :mod:`Context` for this:

.. code-block:: Python

   from otools import Context, LoggingLevel

   context = Context(level = LoggingLevel.INFO, name = "MyContext")

.. module:: Dataframe
   :synopsis: Dataframe is an object that works like shared memory space

:mod:`Dataframe`
~~~~~~~~~~~~~~~~

The :mod:`Dataframe` is an object that's meant to work like shared memory space. You
can set multiple values to different keys and get them from every :mod:`Service`
attached to the same :mod:`Context` as the one containing the :mod:`Dataframe`.

:mod:`Dataframe` objects can be attached to multiple :mod:`Context` objects in order to
share it among everything you need.

.. function:: __init__ (name = "Dataframe")
   
   The constructor sets as default *Dataframe* as the name of the object. Remember
   that there can't be two :mod:`Dataframe` objects with the same name attached to the
   same :mod:`Context` object.

.. function:: get (key, blockReading=False, blockWriting=True, timeout=-1)
   
   This function gets the value of the key *key* attached to this :mod:`Dataframe`
   object. If the key is not set, it logs an error message and returns *None*.

   The *blockReading* and *blockWriting* flags are used to set if the locks for
   reading and writing of the :mod:`Dataframe` are acquired on this *get*. The
   *timeout* is how long it should wait for acquiring those locks, in case it needs to wait.

   By default, on the *get* function, reading is not blocked but writing is. Timeout
   is infinite.

   **Note**: all locks are released automatically by the framework.

.. function:: set (key, value, blockReading=True, blockWriting=True, timeout=-1)
   
   Similar to the function *get* on the parameters and explanation. The only different
   parameter here is *value*, which is the value you want to set to the key *key*.

**Best practices**:

* If you need a function to return a value for you to set it into a key, *DO NOT* do this:

   .. code-block:: Python

      dataframe.set('myKey', function(myArgs))

   because you will lock your dataframe until your *function* returns. This happening,
   every other module that needs access to this dataframe will be locked too.

   The best to do in this scenario is:

   .. code-block:: Python

      value = function(myArgs)
      dataframe.set('myKey', value)

   as this won't hold the dataframe until the function returns.

**Continuing the example**:

For the sake of simplicity, I'll construct just one :mod:`Dataframe` and attach it into
the single :mod:`Context` we've built before:

.. code-block:: Python

   from otools import Dataframe

   dataframe = Dataframe(name = "MyDataframe")
   context += dataframe

.. module:: Service
   :synopsis: Service is a metaclass for making your code work in threads and communicate with other modules

:mod:`Service`
~~~~~~~~~~~~~~

A Service is a metaclass that shall encapsulate your own code in order to attach it into a 
:mod:`Context` object. As it encapsulates another class, it will make few methods available
for it, in order to interact with the framework.

The class that will be encapsulated can implement few methods of its own that will interact
with the framework. They're:

* *setup*: this method will set your class up by configuring your environment and everything you need to do before running it;
* *main*: this method will run once for every loop in the :mod:`Context` execution;
* *loop*: this method will run in loop in an exclusive thread, not depending on the :mod:`Context` execution loop;
* *finalize*: this method is the shutting down procedure, it says what your class should do before ending.

The way these methods interact with the framework will get clearer when we get to our orchestrator, :mod:`OTools`.

Methods that will be available for the class after encapsulation are the following:

.. function:: MSG_VERBOSE (message, moduleName="Unknown", contextName="Unknown", *args, **kws)
   
   Log a message with level *LoggingLevel.VERBOSE*. *moduleName* and *contextName* will
   be filled by other modules on the framework.

.. function:: MSG_DEBUG (message, moduleName="Unknown", contextName="Unknown", *args, **kws)
   
   Log a message with level *LoggingLevel.DEBUG*. *moduleName* and *contextName* will
   be filled by other modules on the framework.

.. function:: MSG_INFO (message, moduleName="Unknown", contextName="Unknown", *args, **kws)
   
   Log a message with level *LoggingLevel.INFO*. *moduleName* and *contextName* will
   be filled by other modules on the framework.

.. function:: MSG_WARNING (message, moduleName="Unknown", contextName="Unknown", *args, **kws)
   
   Log a message with level *LoggingLevel.WARNING*. *moduleName* and *contextName* will
   be filled by other modules on the framework.

.. function:: MSG_ERROR (message, moduleName="Unknown", contextName="Unknown", *args, **kws)
   
   Log a message with level *LoggingLevel.ERROR*. *moduleName* and *contextName* will
   be filled by other modules on the framework.

.. function:: MSG_FATAL (message, moduleName="Unknown", contextName="Unknown", *args, **kws)
   
   Log a message with level *LoggingLevel.FATAL*. *moduleName* and *contextName* will
   be filled by other modules on the framework.

.. function:: getContext ()
   
   Returns the :mod:`Context` object to which your :mod:`Service` is attached.

.. function:: deactivate ()
   
   Shuts this :mod:`Service` down without interfering on the :mod:`Context`.

.. function:: reset ()
   
   This method is used by the :mod:`Watchdog` module. It resets this single :mod:`Service`
   by re-creating it over itself.

.. function:: terminateContext ()
   
   This method shuts everything down on the :mod:`Context`. If this is the only :mod:`Context`
   running, this will shutdown the framework.

.. function:: getService (serviceName)
   
   This will return the :mod:`Service` object identified by the name *serviceName*
   attached to the :mod:`Context`.

.. function:: getDataframe (dataframeName)
   
   This will return the :mod:`Dataframe` object identified by the name *dataframeName*
   attached to the :mod:`Context`.

Besides those methods that will be available for your class, the :mod:`Service` object
also has few of their own:

.. function:: setup ()
   
   This will run the *setup* method of your own class.

.. function:: main ()
   
   This will run the *main* method of your own class.

.. function:: loop ()
   
   This will feed the :mod:`Watchdog` and run one iteration of
   the *loop* method of your own class.

.. function:: finalize ()
   
   This will run the *finalize* method of your own class and deactivate this.

**Continuing the example**:

For the sake of simplicity, I'll construct just two :mod:`Service` and attach them into
the single :mod:`Context` we've built before:

.. code-block:: Python

   from otools import Service
   from time import sleep

   class MyCode ():
      # All methods here are optional
      def setup (self):
         # Do whatever you need here
         pass
      def main (self):
         # I'll just print something
         self.MSG_INFO("Hey, I'm being executed!")
         sleep(2)
      def loop (self):
         # I'll print here using WARNING level
         self.MSG_WARNING("A warning log here!")
         sleep(1)
      def finalize (self):
         # Stop!
         self.MSG_INFO("Shutting down...")
         pass

   class MySecondCode ():
      def setup(self):
         self.loopCounter = 0
      def main(self):
         self.loopCounter += 1
         if self.loopCounter >= 5:
            self.MSG_INFO("I'm shutting everything down!")
            self.terminateContext()

   context += Service(MyCode)
   context += Service(MySecondCode)

Notice that, when this runs, for every :mod:`Context` execution loop, *MyCode* will log an *INFO* message and *MySecondCode*
will count the number of loops. If the *loopCounter* is equal or greater than 5, *MySecondCode* will terminate the :mod:`Context`.
As this is the only :mod:`Context` running, it will shut the whole software down.

Meanwhile *MyCode* will, in an exclusive thread, print *WARNING* messages until the :mod:`Context` shuts down.

.. module:: Trigger
   :synopsis: Trigger is an object that shall execute a stack of Services when conditions are attended


:mod:`Trigger`
~~~~~~~~~~~~~~

Trigger is a class for implement triggering actions on the framework. After being constructed,
:mod:`Service` and :mod:`TriggerCondition` objects are allowed in order to configure this.

For interacting with :mod:`Trigger` objects, these are the methods you should know:

.. function:: __init__ (name = "Trigger", triggerType = 'or')
   
   When constructing this type of object, as it's similar to :mod:`Service` objects,
   a *name* will be assigned and it must not conflict with any :mod:`Service` names
   attached to the same :mod:`Context`. The *triggerType* allowed options are:

   * *and* : all conditions must trigger;
   * *or*  : any of the conditions must trigger;
   * *xor* : make a XOR on the conditions, in the order they were attached.

.. function:: __add__ (a)
   
   As previously said, only :mod:`Service` and :mod:`TriggerCondition` objects are allowed
   to be attached to :mod:`Trigger` objects.
   
   All :mod:`Service` objects will join the execution stack of the :mod:`Trigger`. Notice that
   *loop* methods will be ignored on :mod:`Trigger` stack executions.

   All :mod:`TriggerCondition` objects will join the list of conditions it must attend according
   to the *triggerType* in order to run the execution stack.

.. module:: TriggerCondition
   :synopsis: TriggerCondition is a class for encapsulating other classes in order to identify it as a condition not as anything else.

A :mod:`TriggerCondition` is a class for encapsulating other classes in order to identify it as a condition not as anything else.
It has only one important method, which is:

.. function:: main ()
   
   This method will run the *main* method of your encapsulated class and the answer (*True* or *False*)
   will say whether this :mod:`TriggerCondition` will trigger or not.

No :mod:`Trigger` objects will be used on our SimpleExample_, but here's a code snippet in order to get
things clearer:

.. code-block:: Python

   from otools import Service, Context, OTools, Trigger, TriggerCondition, Dataframe
   from time import sleep

   class Increment ():
      def main(self):
         df = self.getDataframe('counter')
         if df.get('counter') == None:
            df.set('counter', 0)
         df.set('counter', df.get('counter') + 1)
         sleep(1)
   
   class Shutdown ():
      def main(self):
         self.terminateContext()
   
   class MyCondition ():
      def main(self):
         df = self.getDataframe('counter')
         if df.get('counter') >= 5:
            return True
         else:
            return False

   ctx = Context()

   trigger = Trigger()
   trigger += TriggerCondition(MyCondition)
   trigger += Service(Shutdown)

   df = Dataframe('counter')

   ctx += Service(Increment)
   ctx += trigger
   ctx += df

   main = OTools()
   main += ctx
   main.setup()
   main.run()

.. module:: Watchdog
   :synopsis: Watchdog is a module that allows monitoring Services in order to assure the framework won't stop

:mod:`Watchdog`
~~~~~~~~~~~~~~~

.. module:: OTools
   :synopsis: A framework for online systems

:mod:`OTools`
~~~~~~~~~~~~~
