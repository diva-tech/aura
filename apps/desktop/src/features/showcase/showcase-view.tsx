import {
  Button,
  Badge,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  Input,
  Tooltip,
  Dialog,
  DialogContent,
  DialogFooter,
  Section
} from "@/components/ui";
import {
  Sparkles,
  Search,
  Zap,
  ArrowRight,
  Star,
  Shield,
  Flame,
  Code
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

export const ShowcaseView = (): JSX.Element => {
  const [dialogOpen, setDialogOpen] = useState(false);

  return (
    <div className="space-y-12 pb-12">
      {/* Buttons Section */}
      <Section
        title="Buttons"
        description="Interactive buttons with multiple variants and states"
        icon={<Zap className="h-4 w-4" />}
      >
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Button variant="primary" size="md">
            <Sparkles className="h-4 w-4 mr-2" />
            Primary Button
          </Button>

          <Button variant="secondary" size="md">
            Secondary Button
          </Button>

          <Button variant="accent" size="md">
            Accent Button
          </Button>

          <Button variant="outline" size="md">
            Outline Button
          </Button>

          <Button variant="primary" size="lg" className="col-span-1 sm:col-span-2 lg:col-span-1">
            Large Button
          </Button>

          <Button variant="ghost" size="sm">
            Ghost Button
          </Button>

          <Button variant="danger" size="md">
            Danger Action
          </Button>

          <Button variant="primary" size="icon">
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      </Section>

      {/* Badges Section */}
      <Section
        title="Badges"
        description="Status indicators and tags with semantic colors"
        icon={<Star className="h-4 w-4" />}
      >
        <div className="flex flex-wrap gap-3">
          <Badge variant="default">Default</Badge>
          <Badge variant="primary">Primary</Badge>
          <Badge variant="secondary">Secondary</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="error">Error</Badge>
          <Badge variant="outline">Outline</Badge>

          <Badge variant="primary" size="sm">
            Small Badge
          </Badge>

          <Badge variant="secondary" size="lg">
            Large Badge
          </Badge>
        </div>
      </Section>

      {/* Cards Section */}
      <Section
        title="Cards"
        description="Glassmorphic card containers with multiple styles"
        icon={<Shield className="h-4 w-4" />}
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <Card variant="glass">
            <CardHeader>
              <CardTitle>Glass Card</CardTitle>
              <CardDescription>
                Frosted glass effect with light blur
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-300">
                Perfect for floating content that blends with the background.
              </p>
            </CardContent>
          </Card>

          <Card variant="glass-dark">
            <CardHeader>
              <CardTitle>Dark Glass Card</CardTitle>
              <CardDescription>
                Deeper glass effect for contrast
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-300">
                Use this for important information or primary actions.
              </p>
            </CardContent>
          </Card>

          <Card variant="gradient">
            <CardHeader>
              <CardTitle>Gradient Card</CardTitle>
              <CardDescription>
                Subtle gradient with glassmorphism
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-300">
                Elegant gradient background for visual hierarchy.
              </p>
            </CardContent>
          </Card>

          <Card variant="solid">
            <CardHeader>
              <CardTitle>Solid Card</CardTitle>
              <CardDescription>
                Opaque background for text-heavy content
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-300">
                Best for ensuring text readability and contrast.
              </p>
            </CardContent>
          </Card>
        </div>
      </Section>

      {/* Input Section */}
      <Section
        title="Inputs"
        description="Form inputs with icons and validation states"
        icon={<Code className="h-4 w-4" />}
      >
        <div className="space-y-4 max-w-md">
          <Input
            icon={<Search className="h-4 w-4" />}
            placeholder="Search with icon..."
            iconPosition="left"
          />

          <Input
            placeholder="Input with right icon..."
            icon={<Sparkles className="h-4 w-4" />}
            iconPosition="right"
          />

          <Input
            placeholder="Error state input"
            error
            helperText="This field has an error"
          />

          <Input
            placeholder="With helper text"
            helperText="This is a helpful hint for the user"
          />
        </div>
      </Section>

      {/* Tooltips Section */}
      <Section
        title="Tooltips"
        description="Hover tooltips with different positions"
        icon={<Flame className="h-4 w-4" />}
      >
        <div className="flex flex-wrap gap-8 justify-around p-8 rounded-2xl border border-white/10 bg-white/5">
          <Tooltip content="Top tooltip" side="top">
            <Button variant="secondary" size="sm">
              Top
            </Button>
          </Tooltip>

          <Tooltip content="Bottom tooltip" side="bottom">
            <Button variant="secondary" size="sm">
              Bottom
            </Button>
          </Tooltip>

          <Tooltip content="Left tooltip" side="left">
            <Button variant="secondary" size="sm">
              Left
            </Button>
          </Tooltip>

          <Tooltip content="Right tooltip" side="right">
            <Button variant="secondary" size="sm">
              Right
            </Button>
          </Tooltip>
        </div>
      </Section>

      {/* Dialog Section */}
      <Section
        title="Dialog"
        description="Modal dialog component with animations"
      >
        <Button
          variant="primary"
          onClick={() => setDialogOpen(true)}
        >
          Open Dialog
        </Button>

        <Dialog
          open={dialogOpen}
          onOpenChange={setDialogOpen}
          title="Example Dialog"
          description="This is a modal dialog with animations and styling"
          size="md"
        >
          <DialogContent>
            <p className="text-slate-300">
              This modal demonstrates the dialog component with smooth animations
              and a professional appearance. You can add any content here.
            </p>

            <div className="mt-4 space-y-2">
              <Input placeholder="Enter your name..." />
              <Input placeholder="Enter your email..." type="email" />
            </div>
          </DialogContent>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={() => setDialogOpen(false)}
            >
              Submit
            </Button>
          </DialogFooter>
        </Dialog>
      </Section>

      {/* Animation Showcase */}
      <Section
        title="Animations"
        description="Smooth animations and transitions"
      >
        <div className="grid gap-4 sm:grid-cols-3">
          {[
            { name: "Fade Up", class: "animate-fade-up" },
            { name: "Blur In", class: "animate-blur-in" },
            { name: "Scale In", class: "animate-scale-in" },
            { name: "Slide Right", class: "animate-slide-in-right" },
            { name: "Float", class: "animate-float" },
            { name: "Glow", class: "animate-glow" }
          ].map((anim) => (
            <div
              key={anim.name}
              className={cn(
                "rounded-2xl border border-white/10 bg-gradient-to-br from-cyan-500/20 to-blue-500/10 p-6 text-center",
                anim.class
              )}
            >
              <p className="font-display font-semibold text-white">{anim.name}</p>
            </div>
          ))}
        </div>
      </Section>

      {/* Color Palette */}
      <Section
        title="Color Palette"
        description="Dark futuristic theme colors"
      >
        <div className="grid gap-3 sm:grid-cols-4">
          {[
            { name: "Cyan", color: "bg-cyan-500" },
            { name: "Blue", color: "bg-blue-500" },
            { name: "Indigo", color: "bg-indigo-500" },
            { name: "Purple", color: "bg-purple-500" },
            { name: "Success", color: "bg-green-500" },
            { name: "Warning", color: "bg-amber-500" },
            { name: "Error", color: "bg-red-500" },
            { name: "Slate", color: "bg-slate-400" }
          ].map((item) => (
            <div key={item.name} className="space-y-2">
              <div
                className={cn(
                  "h-20 rounded-2xl border border-white/10 shadow-glow",
                  item.color
                )}
              />
              <p className="text-xs font-medium text-slate-300">{item.name}</p>
            </div>
          ))}
        </div>
      </Section>
    </div>
  );
};
